"""
Serviço de integração com Azure DevOps API.
"""

import base64
import httpx
from fastapi import HTTPException, status
from app.config import get_settings

settings = get_settings()


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

    async def list_projects(self) -> list[dict]:
        """
        Lista projetos da organização.
        """
        url = f"{self.org_url}/_apis/projects?api-version=7.1-preview.1"

        async with httpx.AsyncClient(timeout=10.0) as client:
            # Tentar Autenticação (Basic para PAT, Bearer para OAuth)
            # Como fallback, tentamos Basic primeiro se parecer PAT, mas aqui vamos tentar ambos se falhar?
            # Para simplificar e seguir o padrão do auth.py:

            # 1. Tentar Basic (PAT)
            pat_encoded = base64.b64encode(f":{self.token}".encode()).decode()
            headers = {"Authorization": f"Basic {pat_encoded}"}

            response = await client.get(url, headers=headers)

            if response.status_code == 401:
                # 2. Se falhar, tentar Bearer
                headers = {"Authorization": f"Bearer {self.token}"}
                response = await client.get(url, headers=headers)

            if response.status_code != 200:
                error_msg = response.text
                print(f"Erro Azure API: {response.status_code} - {error_msg}")
                raise HTTPException(
                    status_code=status.HTTP_502_BAD_GATEWAY,
                    detail=f"Erro ao listar projetos do Azure DevOps: {response.status_code}",
                )

            data = response.json()
            return data.get("value", [])
