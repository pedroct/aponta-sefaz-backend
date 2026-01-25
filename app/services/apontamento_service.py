"""
Servico de negocios para Apontamentos.
Inclui integracao com Azure DevOps API para atualizacao do CompletedWork e RemainingWork.
"""

import base64
import logging
import httpx
from uuid import UUID
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.config import get_settings
from app.repositories.apontamento import ApontamentoRepository
from app.schemas.apontamento import ApontamentoCreate, ApontamentoUpdate
from app.services.azure import AzureService
from app.utils.project_id_normalizer import normalize_project_id

settings = get_settings()
logger = logging.getLogger(__name__)


class ApontamentoService:
    """Servico para operacoes de Apontamento com integracao Azure DevOps."""

    def __init__(self, db: Session, token: str | None = None):
        self.db = db
        self.repository = ApontamentoRepository(db)
        self.token = token
        # Para chamadas à API do Azure DevOps, usar PAT do backend
        # O token do usuário (App Token JWT) não tem permissão para atualizar Work Items
        self._azure_api_token = settings.azure_devops_pat or token
        if settings.azure_devops_org_url:
            self.org_url = settings.azure_devops_org_url.rstrip("/")
        else:
            self.org_url = None

    async def _get_work_item_fields(
        self, organization: str, project: str, work_item_id: int
    ) -> dict:
        """
        Obtem os campos de um work item do Azure DevOps.

        Args:
            organization: Nome da organizacao no Azure DevOps.
            project: ID ou nome do projeto.
            work_item_id: ID do work item.

        Returns:
            Dict com os campos do work item.
        """
        if not self._azure_api_token:
            logger.warning("PAT nao disponivel para consultar work item")
            return {}

        url = (
            f"https://dev.azure.com/{organization}/{project}"
            f"/_apis/wit/workitems/{work_item_id}"
            f"?fields=Microsoft.VSTS.Scheduling.OriginalEstimate,"
            f"Microsoft.VSTS.Scheduling.RemainingWork,"
            f"Microsoft.VSTS.Scheduling.CompletedWork"
            f"&api-version=7.1"
        )

        async with httpx.AsyncClient(timeout=10.0) as client:
            # Usar Basic (PAT do backend)
            pat_encoded = base64.b64encode(f":{self._azure_api_token}".encode()).decode()
            headers = {"Authorization": f"Basic {pat_encoded}"}

            response = await client.get(url, headers=headers)

            if response.status_code != 200:
                logger.error(
                    f"Erro ao obter work item {work_item_id}: {response.status_code}"
                )
                return {}

            data = response.json()
            return data.get("fields", {})

    async def _update_work_item_hours(
        self,
        organization: str,
        project: str,
        work_item_id: int,
        completed_work_hours: float,
    ) -> bool:
        """
        Atualiza os campos CompletedWork e RemainingWork de um work item no Azure DevOps.

        Lógica:
        - CompletedWork = valor total de horas apontadas localmente
        - RemainingWork = OriginalEstimate - CompletedWork (mínimo 0)

        Args:
            organization: Nome da organizacao no Azure DevOps.
            project: ID ou nome do projeto.
            work_item_id: ID do work item.
            completed_work_hours: Total de horas completadas (soma de todos os apontamentos).

        Returns:
            True se atualizado com sucesso, False caso contrario.
        """
        if not self._azure_api_token:
            logger.warning("PAT nao disponivel para atualizar work item")
            return False

        # Obter OriginalEstimate do Azure DevOps
        fields = await self._get_work_item_fields(organization, project, work_item_id)
        original_estimate = fields.get("Microsoft.VSTS.Scheduling.OriginalEstimate", 0) or 0

        # Calcular novo RemainingWork: OriginalEstimate - CompletedWork (mínimo 0)
        novo_remaining_work = max(0, original_estimate - completed_work_hours)

        logger.info(
            f"Work item {work_item_id}: OriginalEstimate={original_estimate}h, "
            f"CompletedWork={completed_work_hours}h, RemainingWork={novo_remaining_work}h"
        )

        url = (
            f"https://dev.azure.com/{organization}/{project}"
            f"/_apis/wit/workitems/{work_item_id}"
            f"?api-version=7.1"
        )

        # JSON Patch format para atualizacao
        patch_document = [
            {
                "op": "add",
                "path": "/fields/Microsoft.VSTS.Scheduling.CompletedWork",
                "value": completed_work_hours,
            },
            {
                "op": "add",
                "path": "/fields/Microsoft.VSTS.Scheduling.RemainingWork",
                "value": novo_remaining_work,
            },
        ]

        async with httpx.AsyncClient(timeout=10.0) as client:
            # Usar Basic (PAT do backend)
            pat_encoded = base64.b64encode(f":{self._azure_api_token}".encode()).decode()
            headers = {
                "Authorization": f"Basic {pat_encoded}",
                "Content-Type": "application/json-patch+json",
            }

            response = await client.patch(url, headers=headers, json=patch_document)

            if response.status_code == 200:
                logger.info(
                    f"Work item {work_item_id} atualizado: "
                    f"CompletedWork={completed_work_hours}h, RemainingWork={novo_remaining_work}h"
                )
                return True
            else:
                logger.error(
                    f"Erro ao atualizar work item {work_item_id}: "
                    f"{response.status_code} - {response.text}"
                )
                return False

    async def _recalculate_and_update_azure(
        self,
        organization: str,
        project: str,
        work_item_id: int,
    ) -> None:
        """
        Recalcula o total de horas e atualiza o Azure DevOps.

        Args:
            organization: Nome da organizacao.
            project: ID do projeto.
            work_item_id: ID do work item.
        """
        # Calcular total de horas apontadas para este work item
        total_horas = self.repository.get_totals_by_work_item(
            work_item_id=work_item_id,
            organization_name=organization,
            project_id=project,
        )

        # Atualizar Azure DevOps
        await self._update_work_item_hours(
            organization=organization,
            project=project,
            work_item_id=work_item_id,
            completed_work_hours=total_horas,
        )

    async def _validate_work_item_state(
        self,
        work_item_id: int,
        organization: str,
        project: str,
    ) -> None:
        """
        Valida se o Work Item está em estado que permite lançamento de horas.
        
        Bloqueia lançamentos em Work Items com estado Completed ou Removed.
        
        Args:
            work_item_id: ID do Work Item
            organization: Nome da organização
            project: ID do projeto
            
        Raises:
            HTTPException 422: Se o Work Item estiver fechado (Completed/Removed)
        """
        if not self._azure_api_token:
            logger.warning("PAT não disponível para validar estado do Work Item")
            return
        
        try:
            azure_service = AzureService(token=self._azure_api_token)
            
            # Buscar estado atual do Work Item usando Batch API
            states_data = await azure_service.get_work_items_current_state_batch(
                work_item_ids=[work_item_id],
                organization_name=organization,
                project=project,
            )
            
            if work_item_id not in states_data:
                logger.error(f"Work Item {work_item_id} não encontrado")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Work Item {work_item_id} não encontrado",
                )
            
            wi_data = states_data[work_item_id]
            current_state = wi_data.get("state")
            
            if not current_state:
                logger.warning(f"Estado do Work Item {work_item_id} não disponível")
                return
            
            # Buscar categoria do estado usando Process API
            # Nota: Para simplificar, vamos usar mapeamento padrão
            # Em produção, deveria buscar via Process API
            state_categories_completed = {
                "Done", "Closed", "Entregue", "Corrigido", "Concluído", "Completo"
            }
            state_categories_removed = {
                "Removed", "Cancelado", "Deleted", "Excluído"
            }
            
            if current_state in state_categories_completed:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=f"Não é possível lançar horas em Work Item fechado (estado: {current_state})",
                )
            
            if current_state in state_categories_removed:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=f"Não é possível lançar horas em Work Item cancelado (estado: {current_state})",
                )
                
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Erro ao validar estado do Work Item: {str(e)}")
            # Não bloquear em caso de erro na validação
            return

    async def criar_apontamento(self, apontamento_data: ApontamentoCreate):
        """
        Cria um novo apontamento e atualiza o CompletedWork/RemainingWork no Azure DevOps.

        Args:
            apontamento_data: Dados do apontamento.

        Returns:
            Apontamento criado.
        """
        try:
            # Normalizar project_id para UUID (aceita nome durante transição)
            try:
                normalized_project_id = normalize_project_id(
                    apontamento_data.project_id, self.db
                )
                # Atualizar o project_id normalizado
                apontamento_data.project_id = normalized_project_id
            except ValueError as e:
                logger.warning(f"Falha ao normalizar project_id: {e}")
                # Se falhar a normalização, continua com o valor original
                # O Azure DevOps pode aceitar tanto UUID quanto nome
            
            # Validar se o Work Item está em estado que permite lançamento
            await self._validate_work_item_state(
                work_item_id=apontamento_data.work_item_id,
                organization=apontamento_data.organization_name,
                project=apontamento_data.project_id,
            )
            
            # Criar apontamento no banco
            apontamento = self.repository.create(apontamento_data)

            # Atualizar Azure DevOps com o total de horas
            await self._recalculate_and_update_azure(
                organization=apontamento_data.organization_name,
                project=apontamento_data.project_id,
                work_item_id=apontamento_data.work_item_id,
            )

            return apontamento

        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e),
            )

    async def atualizar_apontamento(
        self, apontamento_id: UUID, apontamento_data: ApontamentoUpdate
    ):
        """
        Atualiza um apontamento existente e recalcula o CompletedWork.

        Args:
            apontamento_id: ID do apontamento.
            apontamento_data: Dados para atualizacao.

        Returns:
            Apontamento atualizado.
        """
        # Obter apontamento antes da atualizacao
        apontamento_anterior = self.repository.get_by_id(apontamento_id)
        if not apontamento_anterior:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Apontamento com ID {apontamento_id} nao encontrado",
            )

        try:
            # Validar se o Work Item está em estado que permite lançamento
            await self._validate_work_item_state(
                work_item_id=apontamento_anterior.work_item_id,
                organization=apontamento_anterior.organization_name,
                project=apontamento_anterior.project_id,
            )
            
            # Atualizar apontamento no banco
            apontamento = self.repository.update(apontamento_id, apontamento_data)

            # Atualizar Azure DevOps com o novo total de horas
            await self._recalculate_and_update_azure(
                organization=apontamento_anterior.organization_name,
                project=apontamento_anterior.project_id,
                work_item_id=apontamento_anterior.work_item_id,
            )

            return apontamento

        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e),
            )

    async def excluir_apontamento(self, apontamento_id: UUID) -> bool:
        """
        Exclui um apontamento e recalcula o CompletedWork.

        Args:
            apontamento_id: ID do apontamento.

        Returns:
            True se excluido com sucesso.
        """
        # Obter dados antes de excluir
        apontamento = self.repository.get_by_id(apontamento_id)
        if not apontamento:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Apontamento com ID {apontamento_id} nao encontrado",
            )

        work_item_id = apontamento.work_item_id
        organization_name = apontamento.organization_name
        project_id = apontamento.project_id

        # Excluir apontamento
        deleted = self.repository.delete(apontamento_id)

        if deleted:
            # Atualizar Azure DevOps com o novo total de horas
            await self._recalculate_and_update_azure(
                organization=organization_name,
                project=project_id,
                work_item_id=work_item_id,
            )

        return deleted

    def listar_por_work_item(
        self,
        work_item_id: int,
        organization_name: str,
        project_id: str,
        skip: int = 0,
        limit: int = 100,
    ):
        """
        Lista apontamentos de um work item.

        Args:
            work_item_id: ID do work item.
            organization_name: Nome da organizacao.
            project_id: ID do projeto.
            skip: Registros a pular.
            limit: Maximo de registros.

        Returns:
            Tupla (lista de apontamentos, total, total_horas, total_formatado).
        """
        apontamentos, total = self.repository.get_by_work_item(
            work_item_id=work_item_id,
            organization_name=organization_name,
            project_id=project_id,
            skip=skip,
            limit=limit,
        )

        total_horas, total_formatado = self.repository.get_totals_formatted_by_work_item(
            work_item_id=work_item_id,
            organization_name=organization_name,
            project_id=project_id,
        )

        return apontamentos, total, total_horas, total_formatado

    async def get_work_item_info(
        self, organization: str, project: str, work_item_id: int
    ) -> dict:
        """
        Obtem informacoes de um work item do Azure DevOps.

        Args:
            organization: Nome da organizacao.
            project: ID do projeto.
            work_item_id: ID do work item.

        Returns:
            Dict com originalEstimate, remainingWork, completedWork.
        """
        fields = await self._get_work_item_fields(organization, project, work_item_id)

        return {
            "originalEstimate": fields.get(
                "Microsoft.VSTS.Scheduling.OriginalEstimate", 0
            ),
            "remainingWork": fields.get("Microsoft.VSTS.Scheduling.RemainingWork", 0),
            "completedWork": fields.get("Microsoft.VSTS.Scheduling.CompletedWork", 0),
        }

    def resumo_por_work_item(
        self, work_item_id: int, organization_name: str, project_id: str
    ) -> dict:
        """
        Retorna resumo completo conforme contrato do frontend.
        """
        return self.repository.get_summary_by_work_item(
            work_item_id=work_item_id,
            organization_name=organization_name,
            project_id=project_id,
        )
