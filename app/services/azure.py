"""
Serviço de integração com Azure DevOps API.
"""

import base64
import re
import httpx
from fastapi import HTTPException, status
from app.config import get_settings

settings = get_settings()


# Cache em memória para ícones oficiais
_WORK_ITEM_ICON_CACHE = {}

import asyncio

async def get_official_work_item_icons(org_name: str, token: str) -> dict:
    """Busca e faz cache dos ícones oficiais do Azure DevOps para a organização."""
    global _WORK_ITEM_ICON_CACHE
    if org_name in _WORK_ITEM_ICON_CACHE:
        return _WORK_ITEM_ICON_CACHE[org_name]

    url = f"https://dev.azure.com/{org_name}/_apis/wit/workitemicons?api-version=7.2-preview.1"
    pat_encoded = base64.b64encode(f":{token}".encode()).decode()
    headers = {"Authorization": f"Basic {pat_encoded}"}
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(url, headers=headers)
        if response.status_code != 200:
            # fallback: retorna dict vazio
            _WORK_ITEM_ICON_CACHE[org_name] = {}
            return {}
        data = response.json()
        icon_map = {icon["id"]: icon["url"] for icon in data.get("value", [])}
        _WORK_ITEM_ICON_CACHE[org_name] = icon_map
        return icon_map

# Ícone padrão genérico (quadrado com cantos arredondados)
_DEFAULT_ICON_SVG = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16"><rect fill="{color}" x="1" y="1" width="14" height="14" rx="2"/></svg>'
_DEFAULT_COLOR = "#888888"



async def get_work_item_icon_data_uri(org_name: str, token: str, work_item_type: str) -> str:
    """Obtém o SVG oficial do tipo de work item e retorna como Data URI (evita CORS)."""
    import urllib.parse
    
    # Mapeamento dos tipos para os IDs oficiais de ícone do Azure DevOps
    # Referência: GET https://dev.azure.com/{organization}/_apis/wit/workitemicons/{icon}?color={color}&v={v}
    type_to_icon_id = {
        "Task": ("icon_clipboard", "F2CB1D"),
        "Bug": ("icon_insect", "CC293D"),
        "Epic": ("icon_crown", "FF7B00"),
        "Feature": ("icon_trophy", "773B93"),
        "User Story": ("icon_book", "009CCC"),
        "Product Backlog Item": ("icon_list", "009CCC"),
        "Issue": ("icon_traffic_cone", "B4009E"),
        "Test Case": ("icon_test_case", "004B50"),
        "Test Plan": ("icon_test_plan", "004B50"),
        "Test Suite": ("icon_test_suite", "004B50"),
    }
    
    # Se não encontrar, usa o ícone padrão do Azure DevOps (clipboard cinza)
    icon_id, color = type_to_icon_id.get(work_item_type, ("icon_clipboard", "888888"))
    icon_url = f"https://dev.azure.com/{org_name}/_apis/wit/workitemicons/{icon_id}?color={color}&v=2&api-version=7.2-preview.1"
    
    # Header de autenticação (necessário para a API de ícones)
    pat_encoded = base64.b64encode(f":{token}".encode()).decode()
    headers = {"Authorization": f"Basic {pat_encoded}"}
    
    async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
        resp = await client.get(icon_url, headers=headers)
        if resp.status_code == 200:
            content_type = resp.headers.get("content-type", "")
            if content_type.startswith("image/svg"):
                svg = resp.text
                encoded = urllib.parse.quote(svg, safe="")
                return f"data:image/svg+xml,{encoded}"
            elif content_type.startswith("image/png"):
                b64 = base64.b64encode(resp.content).decode()
                return f"data:image/png;base64,{b64}"
    
    # Fallback: retorna SVG oficial do clipboard cinza
    fallback_url = f"https://dev.azure.com/{org_name}/_apis/wit/workitemicons/icon_clipboard?color=888888&v=2&api-version=7.2-preview.1"
    async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
        resp = await client.get(fallback_url, headers=headers)
        if resp.status_code == 200 and resp.headers.get("content-type", "").startswith("image/svg"):
            svg = resp.text
            encoded = urllib.parse.quote(svg, safe="")
            return f"data:image/svg+xml,{encoded}"
    
    # Fallback final: SVG genérico inline
    svg = _DEFAULT_ICON_SVG.replace("{color}", f"#{color}")
    encoded = urllib.parse.quote(svg, safe="")
    return f"data:image/svg+xml,{encoded}"


class AzureService:
    def __init__(self, token: str):
        self.token = token
        if settings.azure_devops_org_url:
            self.org_url = settings.azure_devops_org_url.rstrip("/")
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="AZURE_DEVOPS_ORG_URL não configurada no .env",
            )

    def _resolve_org_name(self, organization_name: str | None) -> str:
        """Resolve o nome da organização a partir do parâmetro ou da URL configurada."""
        if organization_name:
            return organization_name

        match = re.search(r"dev\.azure\.com/([^/]+)", self.org_url)
        if match:
            return match.group(1)

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="organization_name é obrigatório quando AZURE_DEVOPS_ORG_URL não é compatível",
        )

    async def _request(self, method: str, url: str, json: dict | None = None) -> httpx.Response:
        """Executa request usando PAT (Basic Auth)."""
        async with httpx.AsyncClient(timeout=10.0) as client:
            pat_encoded = base64.b64encode(f":{self.token}".encode()).decode()
            headers = {"Authorization": f"Basic {pat_encoded}"}

            if json is not None:
                headers["Content-Type"] = "application/json"

            response = await client.request(method, url, headers=headers, json=json)

            return response

    async def list_projects(self) -> list[dict]:
        """
        Lista projetos da organização.
        """
        url = f"{self.org_url}/_apis/projects?api-version=7.1-preview.1"

        response = await self._request("GET", url)

        if response.status_code != 200:
            error_msg = response.text
            print(f"Erro Azure API: {response.status_code} - {error_msg}")
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Erro ao listar projetos do Azure DevOps: {response.status_code}",
            )

        data = response.json()
        return data.get("value", [])

    async def search_work_items(
        self,
        query: str,
        project_id: str | None,
        organization_name: str | None,
        limit: int = 10,
    ) -> list[dict]:
        """Busca work items por ID ou título usando WIQL."""
        if not project_id:
            project_id = "DEV"

        org_name = self._resolve_org_name(organization_name)
        wiql_url = (
            f"https://dev.azure.com/{org_name}/{project_id}"
            f"/_apis/wit/wiql?api-version=7.1"
        )

        safe_query = query.replace("'", "''")
        if safe_query.isdigit():
            wiql = (
                "SELECT [System.Id] FROM WorkItems "
                f"WHERE [System.TeamProject] = '{project_id}' "
                f"AND [System.Id] = {safe_query}"
            )
        else:
            wiql = (
                "SELECT [System.Id] FROM WorkItems "
                f"WHERE [System.TeamProject] = '{project_id}' "
                f"AND [System.Title] CONTAINS '{safe_query}' "
                "ORDER BY [System.ChangedDate] DESC"
            )

        response = await self._request("POST", wiql_url, json={"query": wiql})

        if response.status_code != 200:
            error_msg = response.text
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Erro ao buscar work items: {response.status_code} - {error_msg}",
            )

        data = response.json()
        ids = [item.get("id") for item in data.get("workItems", []) if item.get("id")]
        ids = ids[:limit]

        if not ids:
            return []

        fields = [
            "System.Id",
            "System.Title",
            "System.WorkItemType",
            "System.State",
            "System.TeamProject",
            "Microsoft.VSTS.Scheduling.OriginalEstimate",
            "Microsoft.VSTS.Scheduling.CompletedWork",
            "Microsoft.VSTS.Scheduling.RemainingWork",
        ]

        items_url = (
            f"https://dev.azure.com/{org_name}/{project_id}"
            f"/_apis/wit/workitems?ids={','.join(str(i) for i in ids)}"
            f"&fields={','.join(fields)}&api-version=7.1"
        )

        items_response = await self._request("GET", items_url)
        if items_response.status_code != 200:
            error_msg = items_response.text
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Erro ao obter detalhes dos work items: {items_response.status_code} - {error_msg}",
            )

        items_data = items_response.json().get("value", [])
        results = []
        # Busca os ícones oficiais de forma assíncrona
        icon_tasks = []
        for item in items_data:
            fields_data = item.get("fields", {})
            work_item_type = fields_data.get("System.WorkItemType", "")
            icon_tasks.append(get_work_item_icon_data_uri(org_name, self.token, work_item_type))
        icon_urls = await asyncio.gather(*icon_tasks)
        results = []
        for idx, item in enumerate(items_data):
            fields_data = item.get("fields", {})
            work_item_type = fields_data.get("System.WorkItemType", "")
            results.append(
                {
                    "id": item.get("id"),
                    "title": fields_data.get("System.Title", ""),
                    "type": work_item_type,
                    "project": fields_data.get("System.TeamProject", project_id),
                    "url": item.get("url", ""),
                    "iconUrl": icon_urls[idx],
                    "originalEstimate": fields_data.get(
                        "Microsoft.VSTS.Scheduling.OriginalEstimate"
                    ),
                    "completedWork": fields_data.get(
                        "Microsoft.VSTS.Scheduling.CompletedWork"
                    ),
                    "remainingWork": fields_data.get(
                        "Microsoft.VSTS.Scheduling.RemainingWork"
                    ),
                    "state": fields_data.get("System.State", ""),
                }
            )
        return results
