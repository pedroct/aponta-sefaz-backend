"""
Serviço para operações com Iterations (Sprints) do Azure DevOps.
Integra com a API de Team Settings para listar iterations e seus work items.
"""

import base64
import logging
from typing import Any

import httpx
from sqlalchemy.orm import Session

from app.config import get_settings
from app.schemas.iteration import (
    IterationAttributes,
    IterationResponse,
    IterationsListResponse,
    IterationWorkItemsResponse,
)

settings = get_settings()
logger = logging.getLogger(__name__)


class IterationService:
    """Serviço para operações com Iterations do Azure DevOps."""

    def __init__(self, db: Session, token: str | None = None):
        self.db = db
        self._token_fallback = token
        self._pat_cache: dict[str, str] = {}

    def _get_pat_for_org(self, organization: str) -> str:
        """
        Retorna o PAT para uma organização específica.
        Busca primeiro no banco de dados, depois nas variáveis de ambiente.
        """
        if organization in self._pat_cache:
            return self._pat_cache[organization]

        # 1. Busca no banco de dados
        from app.repositories.organization_pat import OrganizationPatRepository
        repo = OrganizationPatRepository(self.db)
        pat = repo.get_pat_for_organization(organization)

        if pat:
            logger.debug(f"PAT encontrado no banco para {organization}")
            self._pat_cache[organization] = pat
            return pat

        # 2. Fallback: busca nas variáveis de ambiente
        pat = settings.get_pat_for_org(organization)
        if pat:
            logger.debug(f"PAT encontrado nas variáveis de ambiente para {organization}")
            self._pat_cache[organization] = pat
            return pat

        # 3. Fallback final: usa token fornecido na construção
        if self._token_fallback:
            logger.debug(f"Usando token fallback para {organization}")
            return self._token_fallback

        logger.warning(f"Nenhum PAT encontrado para {organization}")
        return ""

    def _get_headers_for_org(self, organization: str) -> dict[str, str]:
        """
        Retorna os headers de autenticação para uma organização.
        Detecta automaticamente se é JWT ou PAT.
        """
        token = self._get_pat_for_org(organization)
        if not token:
            return {}

        is_jwt = token.count(".") == 2
        if is_jwt:
            return {"Authorization": f"Bearer {token}"}
        else:
            pat_encoded = base64.b64encode(f":{token}".encode()).decode()
            return {"Authorization": f"Basic {pat_encoded}"}

    async def list_iterations(
        self,
        organization: str,
        project: str,
        team: str | None = None,
    ) -> IterationsListResponse:
        """
        Lista todas as iterations (sprints) de um projeto/time.

        Args:
            organization: Nome da organização no Azure DevOps.
            project: ID ou nome do projeto.
            team: ID ou nome do time (opcional, usa time padrão se omitido).

        Returns:
            IterationsListResponse com lista de iterations e ID da atual.
        """
        # Construir URL base
        # GET https://dev.azure.com/{organization}/{project}/{team}/_apis/work/teamsettings/iterations
        if team:
            url = (
                f"https://dev.azure.com/{organization}/{project}/{team}"
                f"/_apis/work/teamsettings/iterations?api-version=7.2-preview.1"
            )
        else:
            url = (
                f"https://dev.azure.com/{organization}/{project}"
                f"/_apis/work/teamsettings/iterations?api-version=7.2-preview.1"
            )

        headers = self._get_headers_for_org(organization)
        if not headers:
            logger.warning(f"Sem credenciais para {organization}")
            return IterationsListResponse(count=0, iterations=[], current_iteration_id=None)

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url, headers=headers)

            if response.status_code != 200:
                logger.error(
                    f"Erro ao listar iterations: {response.status_code} - {response.text[:500]}"
                )
                return IterationsListResponse(count=0, iterations=[], current_iteration_id=None)

            data = response.json()

        # Processar response
        iterations: list[IterationResponse] = []
        current_iteration_id: str | None = None

        for item in data.get("value", []):
            attrs = item.get("attributes", {})
            iteration = IterationResponse(
                id=item.get("id", ""),
                name=item.get("name", ""),
                path=item.get("path"),
                url=item.get("url"),
                attributes=IterationAttributes(
                    startDate=attrs.get("startDate"),
                    finishDate=attrs.get("finishDate"),
                    timeFrame=attrs.get("timeFrame"),
                ),
            )
            iterations.append(iteration)

            # Identificar iteration atual
            if attrs.get("timeFrame") == "current":
                current_iteration_id = iteration.id

        return IterationsListResponse(
            count=len(iterations),
            iterations=iterations,
            current_iteration_id=current_iteration_id,
        )

    async def get_iteration_work_items(
        self,
        organization: str,
        project: str,
        iteration_id: str,
        team: str | None = None,
    ) -> IterationWorkItemsResponse:
        """
        Busca os IDs dos Work Items associados a uma iteration.

        Args:
            organization: Nome da organização no Azure DevOps.
            project: ID ou nome do projeto.
            iteration_id: ID (UUID) da iteration.
            team: ID ou nome do time (opcional).

        Returns:
            IterationWorkItemsResponse com lista de IDs dos Work Items.
        """
        # GET https://dev.azure.com/{organization}/{project}/{team}/_apis/work/teamsettings/iterations/{iterationId}/workitems
        if team:
            url = (
                f"https://dev.azure.com/{organization}/{project}/{team}"
                f"/_apis/work/teamsettings/iterations/{iteration_id}/workitems"
                f"?api-version=7.2-preview.1"
            )
        else:
            url = (
                f"https://dev.azure.com/{organization}/{project}"
                f"/_apis/work/teamsettings/iterations/{iteration_id}/workitems"
                f"?api-version=7.2-preview.1"
            )

        headers = self._get_headers_for_org(organization)
        if not headers:
            logger.warning(f"Sem credenciais para {organization}")
            return IterationWorkItemsResponse(
                iteration_id=iteration_id,
                iteration_name="",
                work_item_ids=[],
                count=0,
            )

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url, headers=headers)

            if response.status_code != 200:
                logger.error(
                    f"Erro ao buscar work items da iteration: {response.status_code} - {response.text[:500]}"
                )
                return IterationWorkItemsResponse(
                    iteration_id=iteration_id,
                    iteration_name="",
                    work_item_ids=[],
                    count=0,
                )

            data = response.json()

        # Extrair IDs únicos das relações
        work_item_ids: set[int] = set()
        relations = data.get("workItemRelations", [])

        for relation in relations:
            # target sempre tem o work item
            target = relation.get("target")
            if target and "id" in target:
                work_item_ids.add(target["id"])

            # source pode ter o pai
            source = relation.get("source")
            if source and "id" in source:
                work_item_ids.add(source["id"])

        work_item_ids_list = sorted(list(work_item_ids))

        # Buscar nome da iteration (opcional, para resposta mais completa)
        iteration_name = ""
        iterations = await self.list_iterations(organization, project, team)
        for it in iterations.iterations:
            if it.id == iteration_id:
                iteration_name = it.name
                break

        return IterationWorkItemsResponse(
            iteration_id=iteration_id,
            iteration_name=iteration_name,
            work_item_ids=work_item_ids_list,
            count=len(work_item_ids_list),
        )
