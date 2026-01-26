"""
Serviço de negócios para Timesheet (Folha de Horas).
Monta a hierarquia de Work Items e agrega apontamentos por semana.
"""

import asyncio
import base64
import logging
from datetime import date, timedelta
from typing import Any
from uuid import UUID

import httpx
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.config import get_settings
from app.models.apontamento import Apontamento
from app.repositories.apontamento import duracao_to_decimal, format_duracao
from app.schemas.timesheet import (
    ApontamentoDia,
    CelulaDia,
    ProcessStateMapping,
    StateCategoryResponse,
    TimesheetResponse,
    TotalDia,
    WorkItemRevision,
    WorkItemRevisionFields,
    WorkItemRevisionsResponse,
    WorkItemTimesheet,
)
from app.services.azure import AzureService, get_work_item_icon_data_uri
from app.services.iteration_service import IterationService
from app.utils.project_id_normalizer import normalize_project_id, is_valid_uuid

settings = get_settings()
logger = logging.getLogger(__name__)

# Mapeamento de estados para categorias (Agile Process)
# Ref: https://learn.microsoft.com/en-us/azure/devops/boards/work-items/workflow-and-state-categories
STATE_TO_CATEGORY = {
    # Proposed
    "New": "Proposed",
    # In Progress
    "Active": "InProgress",
    "Committed": "InProgress",
    "Open": "InProgress",
    # Resolved
    "Resolved": "Resolved",
    # Completed
    "Closed": "Completed",
    "Done": "Completed",
    # Removed
    "Removed": "Removed",
}

# Categorias que permitem edição/exclusão
EDITABLE_CATEGORIES = {"Proposed", "InProgress", "Resolved"}

# Mapeamento de tipo para nível hierárquico
TYPE_TO_LEVEL = {
    "Epic": 0,
    "Feature": 1,
    "User Story": 2,
    "Product Backlog Item": 2,
    "Task": 3,
    "Bug": 3,
}

# Dias da semana em português
DIAS_SEMANA_PT = ["seg", "ter", "qua", "qui", "sex", "sáb", "dom"]


def get_week_dates(week_start: date | None = None) -> tuple[date, date, list[date]]:
    """
    Retorna as datas da semana (segunda a domingo).

    Args:
        week_start: Data de início da semana. Se None, usa a semana atual.

    Returns:
        Tupla (inicio, fim, lista_de_datas)
    """
    if week_start is None:
        today = date.today()
        # Encontrar a segunda-feira da semana atual
        week_start = today - timedelta(days=today.weekday())
    else:
        # Garantir que é uma segunda-feira
        week_start = week_start - timedelta(days=week_start.weekday())

    week_end = week_start + timedelta(days=6)
    dates = [week_start + timedelta(days=i) for i in range(7)]

    return week_start, week_end, dates


def get_state_category(state: str) -> str:
    """Retorna a categoria de um estado."""
    return STATE_TO_CATEGORY.get(state, "InProgress")


def can_edit_apontamento(state_category: str) -> bool:
    """Verifica se pode editar apontamentos com base na categoria do estado."""
    return state_category in EDITABLE_CATEGORIES


class TimesheetService:
    """Serviço para operações de Timesheet."""

    def __init__(self, db: Session, token: str | None = None, organization: str | None = None):
        self.db = db
        self._token_fallback = token
        self._organization = organization
        # O PAT será resolvido dinamicamente por organização
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

    @property
    def api_token(self) -> str:
        """Retorna o PAT da organização atual (para retrocompatibilidade)."""
        if self._organization:
            return self._get_pat_for_org(self._organization)
        # Fallback para o PAT padrão das variáveis de ambiente
        return settings.azure_devops_pat or self._token_fallback or ""

    async def _get_work_items_hierarchy(
        self,
        organization: str,
        project: str,
        user_email: str | None = None,
    ) -> list[dict[str, Any]]:
        """
        Busca a hierarquia de Work Items do Azure DevOps usando WIQL recursivo.

        Args:
            organization: Nome da organização.
            project: ID do projeto.
            user_email: Email do usuário para filtro.

        Returns:
            Lista de Work Items com hierarquia.
        """
        if not self._get_pat_for_org(organization):
            logger.warning(f"Token não disponível para buscar work items da organização {organization}")
            return []

        # WIQL para buscar hierarquia (Epic -> Feature -> Story -> Task/Bug)
        wiql_url = (
            f"https://dev.azure.com/{organization}/{project}"
            f"/_apis/wit/wiql?api-version=7.1"
        )

        # Query para buscar links hierárquicos
        # Modo recursivo para pegar toda a árvore
        assigned_filter = ""
        if user_email:
            assigned_filter = f"AND [System.AssignedTo] = '{user_email}' "

        wiql = f"""
        SELECT [System.Id]
        FROM WorkItemLinks
        WHERE (
            [Source].[System.TeamProject] = '{project}'
            AND [Source].[System.WorkItemType] IN ('Epic', 'Feature', 'User Story', 'Product Backlog Item', 'Task', 'Bug')
            {assigned_filter}
        )
        AND ([System.Links.LinkType] = 'System.LinkTypes.Hierarchy-Forward')
        AND (
            [Target].[System.WorkItemType] IN ('Epic', 'Feature', 'User Story', 'Product Backlog Item', 'Task', 'Bug')
        )
        MODE (Recursive)
        """

        async with httpx.AsyncClient(timeout=30.0) as client:
            # Usar headers com o PAT correto para a organização
            headers = self._get_headers_for_org(organization)
            
            if not headers:
                logger.warning(f"Sem credenciais para {organization}")
                return []

            response = await client.post(
                wiql_url, headers=headers, json={"query": wiql}
            )

            if response.status_code != 200:
                logger.error(f"Erro WIQL: {response.status_code} - {response.text[:500]}")
                logger.debug(f"URL: {wiql_url}")
                logger.debug(f"Query: {wiql}")
                # Tentar query simples se a recursiva falhar
                return await self._get_work_items_simple(
                    organization, project, user_email
                )

            data = response.json()

            # Extrair IDs únicos das relações
            work_item_ids = set()
            relations = data.get("workItemRelations", [])

            for relation in relations:
                if relation.get("source"):
                    work_item_ids.add(relation["source"]["id"])
                if relation.get("target"):
                    work_item_ids.add(relation["target"]["id"])

            if not work_item_ids:
                return []

            # Buscar detalhes dos Work Items
            return await self._get_work_items_details(
                organization, project, list(work_item_ids), relations
            )

    async def _get_work_items_simple(
        self,
        organization: str,
        project: str,
        user_email: str | None = None,
    ) -> list[dict[str, Any]]:
        """
        Busca Work Items usando query simples (fallback).
        """
        wiql_url = (
            f"https://dev.azure.com/{organization}/{project}"
            f"/_apis/wit/wiql?api-version=7.1"
        )

        assigned_filter = ""
        if user_email:
            assigned_filter = f"AND [System.AssignedTo] = '{user_email}' "

        wiql = f"""
        SELECT [System.Id]
        FROM WorkItems
        WHERE [System.TeamProject] = '{project}'
        AND [System.WorkItemType] IN ('Epic', 'Feature', 'User Story', 'Product Backlog Item', 'Task', 'Bug')
        AND [System.State] NOT IN ('Removed', 'Closed')
        {assigned_filter}
        ORDER BY [System.WorkItemType], [System.Id]
        """

        async with httpx.AsyncClient(timeout=30.0) as client:
            # Usar headers com o PAT correto para a organização
            headers = self._get_headers_for_org(organization)

            response = await client.post(
                wiql_url, headers=headers, json={"query": wiql}
            )

            if response.status_code != 200:
                logger.error(f"Erro WIQL simples: {response.status_code}")
                return []

            data = response.json()
            work_item_ids = [item["id"] for item in data.get("workItems", [])]

            if not work_item_ids:
                return []

            return await self._get_work_items_details(
                organization, project, work_item_ids, []
            )

    async def _get_work_items_details(
        self,
        organization: str,
        project: str,
        work_item_ids: list[int],
        relations: list[dict],
    ) -> list[dict[str, Any]]:
        """
        Busca detalhes dos Work Items incluindo campos de scheduling.
        """
        if not work_item_ids:
            return []

        # Limitar a 200 IDs por request (limite da API)
        all_items = []
        for i in range(0, len(work_item_ids), 200):
            batch_ids = work_item_ids[i : i + 200]

            fields = [
                "System.Id",
                "System.Title",
                "System.WorkItemType",
                "System.State",
                "System.AssignedTo",
                "System.Parent",
                "Microsoft.VSTS.Scheduling.OriginalEstimate",
                "Microsoft.VSTS.Scheduling.CompletedWork",
                "Microsoft.VSTS.Scheduling.RemainingWork",
            ]

            items_url = (
                f"https://dev.azure.com/{organization}/{project}"
                f"/_apis/wit/workitems?ids={','.join(str(i) for i in batch_ids)}"
                f"&fields={','.join(fields)}&api-version=7.1"
            )

            async with httpx.AsyncClient(timeout=30.0) as client:
                # Usar headers com o PAT correto para a organização
                headers = self._get_headers_for_org(organization)

                response = await client.get(items_url, headers=headers)

                if response.status_code != 200:
                    logger.error(f"Erro ao buscar detalhes: {response.status_code}")
                    continue

                items_data = response.json().get("value", [])

                # Buscar ícones em paralelo
                icon_tasks = []
                pat_for_org = self._get_pat_for_org(organization)
                for item in items_data:
                    work_item_type = item.get("fields", {}).get(
                        "System.WorkItemType", ""
                    )
                    icon_tasks.append(
                        get_work_item_icon_data_uri(organization, pat_for_org or "", work_item_type)
                    )

                icon_urls = await asyncio.gather(*icon_tasks)

                for idx, item in enumerate(items_data):
                    fields_data = item.get("fields", {})
                    state = fields_data.get("System.State", "")
                    state_category = get_state_category(state)

                    assigned_to = fields_data.get("System.AssignedTo", {})
                    if isinstance(assigned_to, dict):
                        assigned_to_name = assigned_to.get("displayName", "")
                    else:
                        assigned_to_name = str(assigned_to) if assigned_to else ""

                    all_items.append(
                        {
                            "id": item.get("id"),
                            "title": fields_data.get("System.Title", ""),
                            "type": fields_data.get("System.WorkItemType", ""),
                            "state": state,
                            "state_category": state_category,
                            "assigned_to": assigned_to_name,
                            "parent_id": fields_data.get("System.Parent"),
                            "icon_url": icon_urls[idx],
                            "original_estimate": fields_data.get(
                                "Microsoft.VSTS.Scheduling.OriginalEstimate"
                            ),
                            "completed_work": fields_data.get(
                                "Microsoft.VSTS.Scheduling.CompletedWork"
                            ),
                            "remaining_work": fields_data.get(
                                "Microsoft.VSTS.Scheduling.RemainingWork"
                            ),
                        }
                    )

        return all_items

    def _get_apontamentos_semana(
        self,
        organization: str,
        project: str,
        week_start: date,
        week_end: date,
        user_id: str | None = None,
    ) -> dict[int, dict[date, list[Apontamento]]]:
        """
        Busca apontamentos da semana agrupados por work_item_id e data.
        
        Durante a transição, aceita tanto UUID quanto nome do projeto.

        Returns:
            Dict[work_item_id, Dict[data, List[Apontamento]]]
        """
        # Normalizar project_id para UUID se possível
        project_normalized = project
        try:
            if not is_valid_uuid(project):
                project_normalized = normalize_project_id(project, self.db)
                logger.info(f"Project ID normalizado: {project} -> {project_normalized}")
        except ValueError as e:
            logger.warning(f"Não foi possível normalizar project_id '{project}': {e}")
        
        # Query que aceita ambos os formatos durante a transição
        query = self.db.query(Apontamento).filter(
            Apontamento.organization_name == organization,
            or_(
                Apontamento.project_id == project_normalized,  # UUID
                Apontamento.project_id == project,  # Formato antigo (fallback)
            ),
            Apontamento.data_apontamento >= week_start,
            Apontamento.data_apontamento <= week_end,
        )

        if user_id:
            query = query.filter(Apontamento.usuario_id == user_id)

        apontamentos = query.all()

        # Agrupar por work_item_id e data
        result: dict[int, dict[date, list[Apontamento]]] = {}
        for apt in apontamentos:
            wi_id: int = apt.work_item_id  # type: ignore
            data_apt: date = apt.data_apontamento  # type: ignore
            if wi_id not in result:
                result[wi_id] = {}
            if data_apt not in result[wi_id]:
                result[wi_id][data_apt] = []
            result[wi_id][data_apt].append(apt)

        return result

    def _build_work_item_timesheet(
        self,
        work_item: dict[str, Any],
        week_dates: list[date],
        apontamentos_map: dict[int, dict[date, list[Apontamento]]],
        today: date,
    ) -> WorkItemTimesheet:
        """
        Constrói o objeto WorkItemTimesheet com células e totais.
        """
        work_item_id = work_item["id"]
        state_category = work_item.get("state_category", "InProgress")
        pode_editar = can_edit_apontamento(state_category)

        # Construir células dos dias
        dias: list[CelulaDia] = []
        total_semana = 0.0
        apontamentos_work_item = apontamentos_map.get(work_item_id, {})

        for i, dt in enumerate(week_dates):
            dia_apontamentos = apontamentos_work_item.get(dt, [])

            # Calcular total do dia
            total_dia = sum(
                duracao_to_decimal(str(apt.duracao)) for apt in dia_apontamentos
            )
            total_semana += total_dia

            # Converter apontamentos para schema
            apontamentos_dia = [
                ApontamentoDia(
                    id=apt.id,  # type: ignore
                    duracao=str(apt.duracao),
                    duracao_horas=duracao_to_decimal(str(apt.duracao)),
                    id_atividade=apt.id_atividade,  # type: ignore
                    atividade_nome=apt.atividade.nome if apt.atividade else "",
                    comentario=str(apt.comentario) if apt.comentario is not None else None,
                )
                for apt in dia_apontamentos
            ]

            celula = CelulaDia(
                data=dt,
                dia_semana=DIAS_SEMANA_PT[i],
                dia_numero=dt.day,
                total_horas=total_dia,
                total_formatado=format_duracao(int(total_dia * 60)) if total_dia > 0 else "",
                apontamentos=apontamentos_dia,
                eh_hoje=dt == today,
                eh_fim_semana=i >= 5,  # sábado e domingo
            )
            dias.append(celula)

        return WorkItemTimesheet(
            id=work_item_id,
            title=work_item.get("title", ""),
            type=work_item.get("type", ""),
            state=work_item.get("state", ""),
            state_category=state_category,
            icon_url=work_item.get("icon_url", ""),
            assigned_to=work_item.get("assigned_to"),
            original_estimate=work_item.get("original_estimate"),
            completed_work=work_item.get("completed_work"),
            remaining_work=work_item.get("remaining_work"),
            total_semana_horas=total_semana,
            total_semana_formatado=format_duracao(int(total_semana * 60)) if total_semana > 0 else "",
            dias=dias,
            nivel=TYPE_TO_LEVEL.get(work_item.get("type", ""), 3),
            parent_id=work_item.get("parent_id"),
            children=[],
            pode_editar=pode_editar,
            pode_excluir=pode_editar,
        )

    def _build_hierarchy(
        self, work_items: list[WorkItemTimesheet]
    ) -> list[WorkItemTimesheet]:
        """
        Constrói a árvore hierárquica de Work Items.
        """
        # Criar mapa de ID para item
        items_map = {item.id: item for item in work_items}

        # Identificar raízes e construir árvore
        roots: list[WorkItemTimesheet] = []

        for item in work_items:
            if item.parent_id and item.parent_id in items_map:
                parent = items_map[item.parent_id]
                parent.children.append(item)
            else:
                roots.append(item)

        # Ordenar por tipo (Epic > Feature > Story > Task)
        def sort_key(item: WorkItemTimesheet) -> tuple:
            return (item.nivel, item.id)

        for item in items_map.values():
            item.children.sort(key=sort_key)

        roots.sort(key=sort_key)

        return roots

    async def get_timesheet(
        self,
        organization: str,
        project: str,
        week_start: date | None = None,
        user_email: str | None = None,
        user_id: str | None = None,
        iteration_id: str | None = None,
    ) -> TimesheetResponse:
        """
        Retorna o timesheet completo para uma semana.

        Args:
            organization: Nome da organização Azure DevOps.
            project: ID do projeto.
            week_start: Início da semana (segunda). Se None, usa semana atual.
            user_email: Email do usuário para filtro.
            user_id: ID do usuário para filtrar apontamentos.
            iteration_id: ID da iteration (sprint) para filtrar work items.

        Returns:
            TimesheetResponse com a hierarquia e totais.
        """
        # Determinar datas da semana
        week_start_date, week_end_date, week_dates = get_week_dates(week_start)
        today = date.today()

        # Se iteration_id fornecido, buscar IDs dos work items da iteration
        iteration_work_item_ids: set[int] | None = None
        if iteration_id:
            iteration_service = IterationService(self.db, token=self._token_fallback)
            iteration_work_items = await iteration_service.get_iteration_work_items(
                organization=organization,
                project=project,
                iteration_id=iteration_id,
            )
            if iteration_work_items.work_item_ids:
                iteration_work_item_ids = set(iteration_work_items.work_item_ids)
                logger.info(
                    f"Filtrando por iteration {iteration_id}: {len(iteration_work_item_ids)} work items"
                )

        # Buscar Work Items do Azure DevOps
        work_items_data = await self._get_work_items_hierarchy(
            organization, project, user_email
        )

        # Filtrar work items pela iteration, se especificada
        if iteration_work_item_ids is not None:
            work_items_data = [
                wi for wi in work_items_data
                if wi["id"] in iteration_work_item_ids
            ]
            logger.info(f"Work items após filtro de iteration: {len(work_items_data)}")

        # Buscar apontamentos da semana
        apontamentos_map = self._get_apontamentos_semana(
            organization, project, week_start_date, week_end_date
        )

        # Construir objetos WorkItemTimesheet
        work_items_timesheet = [
            self._build_work_item_timesheet(wi, week_dates, apontamentos_map, today)
            for wi in work_items_data
        ]

        # Construir hierarquia
        hierarchy = self._build_hierarchy(work_items_timesheet)

        # Calcular totais por dia
        totais_por_dia: list[TotalDia] = []
        for i, dt in enumerate(week_dates):
            total_dia = sum(
                sum(duracao_to_decimal(str(apt.duracao)) for apt in apts)
                for wi_apts in apontamentos_map.values()
                for d, apts in wi_apts.items()
                if d == dt
            )
            totais_por_dia.append(
                TotalDia(
                    data=dt,
                    dia_semana=DIAS_SEMANA_PT[i],
                    dia_numero=dt.day,
                    total_horas=total_dia,
                    total_formatado=format_duracao(int(total_dia * 60)) if total_dia > 0 else "",
                    eh_hoje=dt == today,
                )
            )

        # Calcular totais gerais
        total_geral = sum(t.total_horas for t in totais_por_dia)
        total_esforco = sum(
            wi.get("original_estimate", 0) or 0 for wi in work_items_data
        )
        total_historico = total_geral  # H = soma da semana atual

        # Label da semana
        semana_label = f"{week_start_date.strftime('%d/%m')} - {week_end_date.strftime('%d/%m')}"

        return TimesheetResponse(
            semana_inicio=week_start_date,
            semana_fim=week_end_date,
            semana_label=semana_label,
            work_items=hierarchy,
            total_geral_horas=total_geral,
            total_geral_formatado=format_duracao(int(total_geral * 60)) if total_geral > 0 else "",
            totais_por_dia=totais_por_dia,
            total_work_items=len(work_items_data),
            total_esforco=total_esforco,
            total_historico=total_historico,
        )

    async def get_state_category(
        self, organization: str, project: str, work_item_id: int
    ) -> StateCategoryResponse:
        """
        Retorna a categoria de estado de um Work Item específico.

        Args:
            organization: Nome da organização.
            project: ID do projeto.
            work_item_id: ID do Work Item.

        Returns:
            StateCategoryResponse com permissões de edição.
        """
        pat = self._get_pat_for_org(organization)
        if not pat:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Token não disponível para organização {organization}",
            )

        # Buscar estado do Work Item
        url = (
            f"https://dev.azure.com/{organization}/{project}"
            f"/_apis/wit/workitems/{work_item_id}"
            f"?fields=System.State&api-version=7.1"
        )

        async with httpx.AsyncClient(timeout=10.0) as client:
            # Usar headers com o PAT correto para a organização
            headers = self._get_headers_for_org(organization)

            response = await client.get(url, headers=headers)

            if response.status_code == 404:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Work Item {work_item_id} não encontrado",
                )

            if response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_502_BAD_GATEWAY,
                    detail=f"Erro ao buscar Work Item: {response.status_code}",
                )

            data = response.json()
            state = data.get("fields", {}).get("System.State", "")
            state_category = get_state_category(state)
            can_edit = can_edit_apontamento(state_category)

            return StateCategoryResponse(
                work_item_id=work_item_id,
                state=state,
                state_category=state_category,
                can_edit=can_edit,
                can_delete=can_edit,
            )

    async def get_work_item_revisions(
        self,
        organization: str,
        project: str,
        work_item_id: int,
    ) -> WorkItemRevisionsResponse:
        """
        Busca o histórico de revisões de um Work Item.
        
        Args:
            organization: Nome da organização
            project: ID do projeto
            work_item_id: ID do Work Item
            
        Returns:
            WorkItemRevisionsResponse com lista de revisões
        """
        azure_service = AzureService(token=self._get_pat_for_org(organization))
        
        revisions_data = await azure_service.get_work_item_revisions(
            work_item_id=work_item_id,
            organization_name=organization,
            project=project,
        )
        
        # Converter para o schema Pydantic
        revisions = [
            WorkItemRevision(
                rev=rev["rev"],
                fields=WorkItemRevisionFields(
                    **{"System.ChangedDate": rev["fields"]["System.ChangedDate"],
                       "System.State": rev["fields"]["System.State"],
                       "System.AssignedTo": rev["fields"]["System.AssignedTo"]}
                )
            )
            for rev in revisions_data
        ]
        
        return WorkItemRevisionsResponse(
            work_item_id=work_item_id,
            revisions=revisions,
        )

    async def get_process_states(
        self,
        organization: str,
        process_id: str,
        work_item_type_ref_name: str,
    ) -> ProcessStateMapping:
        """
        Busca o mapeamento de estados para categorias de um processo.
        
        Args:
            organization: Nome da organização
            process_id: ID do processo (GUID)
            work_item_type_ref_name: Nome de referência do tipo de WI
            
        Returns:
            ProcessStateMapping com dicionário estado -> categoria
        """
        azure_service = AzureService(token=self._get_pat_for_org(organization))
        
        state_map = await azure_service.get_process_work_item_states(
            process_id=process_id,
            work_item_type_ref_name=work_item_type_ref_name,
            organization_name=organization,
        )
        
        return ProcessStateMapping(state_map=state_map)

    async def get_work_items_current_state(
        self,
        work_item_ids: list[int],
        organization: str,
        project: str | None = None,
    ) -> dict[int, dict]:
        """
        Busca o estado atual de múltiplos Work Items usando Batch API.
        
        Args:
            work_item_ids: Lista de IDs dos Work Items
            organization: Nome da organização
            project: Nome do projeto (opcional)
            
        Returns:
            Dicionário mapeando work_item_id -> {id, state, type, assigned_to}
        """
        if not work_item_ids:
            return {}
        
        azure_service = AzureService(token=self._get_pat_for_org(organization))
        
        return await azure_service.get_work_items_current_state_batch(
            work_item_ids=work_item_ids,
            organization_name=organization,
            project=project,
        )
