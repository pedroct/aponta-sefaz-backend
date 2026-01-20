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
from app.repositories.apontamento import (
    ApontamentoRepository,
    parse_duracao,
)
from app.schemas.apontamento import ApontamentoCreate, ApontamentoUpdate

settings = get_settings()
logger = logging.getLogger(__name__)


class ApontamentoService:
    """Servico para operacoes de Apontamento com integracao Azure DevOps."""

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
        Obtem os campos de um work item do Azure DevOps.

        Args:
            organization: Nome da organizacao no Azure DevOps.
            project: ID ou nome do projeto.
            work_item_id: ID do work item.

        Returns:
            Dict com os campos do work item.
        """
        if not self.token:
            logger.warning("Token nao disponivel para consultar work item")
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
            # Usar Basic (PAT)
            pat_encoded = base64.b64encode(f":{self.token}".encode()).decode()
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
        horas_apontamento: float,
    ) -> bool:
        """
        Atualiza os campos CompletedWork e RemainingWork de um work item no Azure DevOps.

        Conforme especificacao:
        - CompletedWork = valor total de horas apontadas localmente
        - RemainingWork = (Valor Atual na Azure - Horas do Apontamento, minimo 0)

        Args:
            organization: Nome da organizacao no Azure DevOps.
            project: ID ou nome do projeto.
            work_item_id: ID do work item.
            completed_work_hours: Total de horas completadas (soma local).
            horas_apontamento: Horas do apontamento atual (para calculo do RemainingWork).

        Returns:
            True se atualizado com sucesso, False caso contrario.
        """
        if not self.token:
            logger.warning("Token nao disponivel para atualizar work item")
            return False

        # Primeiro, obter o RemainingWork atual do Azure
        fields = await self._get_work_item_fields(organization, project, work_item_id)
        remaining_work_atual = fields.get("Microsoft.VSTS.Scheduling.RemainingWork", 0) or 0

        # Calcular novo RemainingWork (nao pode ser negativo)
        novo_remaining_work = max(0, remaining_work_atual - horas_apontamento)

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
            # Usar Basic (PAT)
            pat_encoded = base64.b64encode(f":{self.token}".encode()).decode()
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
        horas_delta: float = 0,
    ) -> None:
        """
        Recalcula o total de horas e atualiza o Azure DevOps.

        Args:
            organization: Nome da organizacao.
            project: ID do projeto.
            work_item_id: ID do work item.
            horas_delta: Horas do apontamento adicionado/removido (para calculo do RemainingWork).
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
            horas_apontamento=horas_delta,
        )

    async def criar_apontamento(self, apontamento_data: ApontamentoCreate):
        """
        Cria um novo apontamento e atualiza o CompletedWork/RemainingWork no Azure DevOps.

        Args:
            apontamento_data: Dados do apontamento.

        Returns:
            Apontamento criado.
        """
        try:
            # Criar apontamento no banco
            apontamento = self.repository.create(apontamento_data)

            # Calcular horas do apontamento para o delta do RemainingWork
            horas, minutos = parse_duracao(apontamento_data.duracao)
            horas_apontamento = horas + (minutos / 60)

            # Atualizar Azure DevOps
            await self._recalculate_and_update_azure(
                organization=apontamento_data.organization_name,
                project=apontamento_data.project_id,
                work_item_id=apontamento_data.work_item_id,
                horas_delta=horas_apontamento,
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

        # Calcular delta de horas se a duracao mudou
        horas_delta = 0
        if apontamento_data.duracao:
            horas_ant, min_ant = parse_duracao(apontamento_anterior.duracao)
            horas_nova, min_nova = parse_duracao(apontamento_data.duracao)
            horas_delta = (horas_nova + min_nova / 60) - (horas_ant + min_ant / 60)

        try:
            # Atualizar apontamento no banco
            apontamento = self.repository.update(apontamento_id, apontamento_data)

            # Atualizar Azure DevOps (o delta pode ser positivo ou negativo)
            await self._recalculate_and_update_azure(
                organization=apontamento_anterior.organization_name,
                project=apontamento_anterior.project_id,
                work_item_id=apontamento_anterior.work_item_id,
                horas_delta=horas_delta,
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

        # Calcular horas que serao removidas (delta negativo para o RemainingWork)
        horas, minutos = parse_duracao(apontamento.duracao)
        horas_removidas = -(horas + minutos / 60)  # Negativo porque estamos removendo

        # Excluir apontamento
        deleted = self.repository.delete(apontamento_id)

        if deleted:
            # Atualizar Azure DevOps
            # Nota: O RemainingWork aumenta quando removemos horas
            await self._recalculate_and_update_azure(
                organization=organization_name,
                project=project_id,
                work_item_id=work_item_id,
                horas_delta=horas_removidas,
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
