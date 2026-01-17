"""
Serviço de negócios para Apontamentos.
Inclui integração com Azure DevOps API para atualização do CompletedWork.
"""

import base64
import logging
import httpx
from uuid import UUID
from datetime import date
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.config import get_settings
from app.repositories.apontamento import ApontamentoRepository
from app.schemas.apontamento import ApontamentoCreate, ApontamentoUpdate

settings = get_settings()
logger = logging.getLogger(__name__)


class ApontamentoService:
    """Serviço para operações de Apontamento com integração Azure DevOps."""

    def __init__(self, db: Session, token: str | None = None):
        self.db = db
        self.repository = ApontamentoRepository(db)
        self.token = token
        if settings.azure_devops_org_url:
            self.org_url = settings.azure_devops_org_url.rstrip("/")
        else:
            self.org_url = None

    async def _get_work_item_fields(
        self, organization: str, project: str, work_item_id: int
    ) -> dict:
        """
        Obtém os campos de um work item do Azure DevOps.

        Args:
            organization: Nome da organização no Azure DevOps.
            project: ID ou nome do projeto.
            work_item_id: ID do work item.

        Returns:
            Dict com os campos do work item.
        """
        if not self.token:
            logger.warning("Token não disponível para consultar work item")
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
            # Tentar Basic (PAT) primeiro
            pat_encoded = base64.b64encode(f":{self.token}".encode()).decode()
            headers = {"Authorization": f"Basic {pat_encoded}"}

            response = await client.get(url, headers=headers)

            if response.status_code == 401:
                # Tentar Bearer
                headers = {"Authorization": f"Bearer {self.token}"}
                response = await client.get(url, headers=headers)

            if response.status_code != 200:
                logger.error(
                    f"Erro ao obter work item {work_item_id}: {response.status_code}"
                )
                return {}

            data = response.json()
            return data.get("fields", {})

    async def _update_completed_work(
        self,
        organization: str,
        project: str,
        work_item_id: int,
        completed_work_hours: float,
    ) -> bool:
        """
        Atualiza o campo CompletedWork de um work item no Azure DevOps.

        Args:
            organization: Nome da organização no Azure DevOps.
            project: ID ou nome do projeto.
            work_item_id: ID do work item.
            completed_work_hours: Total de horas completadas.

        Returns:
            True se atualizado com sucesso, False caso contrário.
        """
        if not self.token:
            logger.warning("Token não disponível para atualizar work item")
            return False

        url = (
            f"https://dev.azure.com/{organization}/{project}"
            f"/_apis/wit/workitems/{work_item_id}"
            f"?api-version=7.1"
        )

        # JSON Patch format para atualização
        patch_document = [
            {
                "op": "add",
                "path": "/fields/Microsoft.VSTS.Scheduling.CompletedWork",
                "value": completed_work_hours,
            }
        ]

        async with httpx.AsyncClient(timeout=10.0) as client:
            # Tentar Basic (PAT) primeiro
            pat_encoded = base64.b64encode(f":{self.token}".encode()).decode()
            headers = {
                "Authorization": f"Basic {pat_encoded}",
                "Content-Type": "application/json-patch+json",
            }

            response = await client.patch(url, headers=headers, json=patch_document)

            if response.status_code == 401:
                # Tentar Bearer
                headers = {
                    "Authorization": f"Bearer {self.token}",
                    "Content-Type": "application/json-patch+json",
                }
                response = await client.patch(url, headers=headers, json=patch_document)

            if response.status_code == 200:
                logger.info(
                    f"CompletedWork atualizado para {completed_work_hours}h no work item {work_item_id}"
                )
                return True
            else:
                logger.error(
                    f"Erro ao atualizar CompletedWork do work item {work_item_id}: "
                    f"{response.status_code} - {response.text}"
                )
                return False

    def _calculate_total_hours(self, total_horas: int, total_minutos: int) -> float:
        """
        Calcula o total em horas decimais.

        Args:
            total_horas: Total de horas inteiras.
            total_minutos: Total de minutos.

        Returns:
            Total em horas decimais.
        """
        # Converter minutos extras em horas
        horas_extras = total_minutos // 60
        minutos_restantes = total_minutos % 60

        total_final_horas = total_horas + horas_extras
        # Converter minutos em fração de hora
        fração_hora = minutos_restantes / 60

        return total_final_horas + fração_hora

    async def criar_apontamento(self, apontamento_data: ApontamentoCreate):
        """
        Cria um novo apontamento e atualiza o CompletedWork no Azure DevOps.

        Args:
            apontamento_data: Dados do apontamento.

        Returns:
            Apontamento criado.
        """
        try:
            # Criar apontamento no banco
            apontamento = self.repository.create(apontamento_data)

            # Calcular total de horas apontadas para este work item
            total_horas, total_minutos = self.repository.get_totals_by_work_item(
                work_item_id=apontamento_data.work_item_id,
                organization_name=apontamento_data.organization_name,
                project_id=apontamento_data.project_id,
            )

            # Converter para horas decimais
            completed_work = self._calculate_total_hours(total_horas, total_minutos)

            # Atualizar CompletedWork no Azure DevOps
            await self._update_completed_work(
                organization=apontamento_data.organization_name,
                project=apontamento_data.project_id,
                work_item_id=apontamento_data.work_item_id,
                completed_work_hours=completed_work,
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
            apontamento_data: Dados para atualização.

        Returns:
            Apontamento atualizado.
        """
        # Obter apontamento antes da atualização para ter os dados do work item
        apontamento_anterior = self.repository.get_by_id(apontamento_id)
        if not apontamento_anterior:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Apontamento com ID {apontamento_id} não encontrado",
            )

        try:
            # Atualizar apontamento no banco
            apontamento = self.repository.update(apontamento_id, apontamento_data)

            # Recalcular total de horas
            total_horas, total_minutos = self.repository.get_totals_by_work_item(
                work_item_id=apontamento_anterior.work_item_id,
                organization_name=apontamento_anterior.organization_name,
                project_id=apontamento_anterior.project_id,
            )

            # Converter para horas decimais
            completed_work = self._calculate_total_hours(total_horas, total_minutos)

            # Atualizar CompletedWork no Azure DevOps
            await self._update_completed_work(
                organization=apontamento_anterior.organization_name,
                project=apontamento_anterior.project_id,
                work_item_id=apontamento_anterior.work_item_id,
                completed_work_hours=completed_work,
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
            True se excluído com sucesso.
        """
        # Obter dados antes de excluir
        apontamento = self.repository.get_by_id(apontamento_id)
        if not apontamento:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Apontamento com ID {apontamento_id} não encontrado",
            )

        work_item_id = apontamento.work_item_id
        organization_name = apontamento.organization_name
        project_id = apontamento.project_id

        # Excluir apontamento
        deleted = self.repository.delete(apontamento_id)

        if deleted:
            # Recalcular total de horas
            total_horas, total_minutos = self.repository.get_totals_by_work_item(
                work_item_id=work_item_id,
                organization_name=organization_name,
                project_id=project_id,
            )

            # Converter para horas decimais
            completed_work = self._calculate_total_hours(total_horas, total_minutos)

            # Atualizar CompletedWork no Azure DevOps
            await self._update_completed_work(
                organization=organization_name,
                project=project_id,
                work_item_id=work_item_id,
                completed_work_hours=completed_work,
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
            organization_name: Nome da organização.
            project_id: ID do projeto.
            skip: Registros a pular.
            limit: Máximo de registros.

        Returns:
            Tupla (lista de apontamentos, total, total_horas, total_minutos).
        """
        apontamentos, total = self.repository.get_by_work_item(
            work_item_id=work_item_id,
            organization_name=organization_name,
            project_id=project_id,
            skip=skip,
            limit=limit,
        )

        total_horas, total_minutos = self.repository.get_totals_by_work_item(
            work_item_id=work_item_id,
            organization_name=organization_name,
            project_id=project_id,
        )

        return apontamentos, total, total_horas, total_minutos

    async def get_work_item_info(
        self, organization: str, project: str, work_item_id: int
    ) -> dict:
        """
        Obtém informações de um work item do Azure DevOps.

        Args:
            organization: Nome da organização.
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
