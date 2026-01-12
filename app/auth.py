"""
Módulo de autenticação Azure DevOps.
Suporta autenticação via:
- Bearer Token (Azure DevOps Extension SDK)
- Personal Access Token (PAT) para desenvolvimento
"""

import base64
import logging
import httpx
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.config import get_settings

# Configurar logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

settings = get_settings()

# Security scheme para Swagger UI
security = HTTPBearer(auto_error=False)


class AzureDevOpsUser:
    """Representa um usuário autenticado do Azure DevOps."""

    def __init__(
        self,
        id: str,
        display_name: str,
        email: str | None = None,
        token: str | None = None,
    ):
        self.id = id
        self.display_name = display_name
        self.email = email
        self.token = token

    def __repr__(self) -> str:
        return f"<AzureDevOpsUser(id={self.id}, name='{self.display_name}')>"


async def validate_azure_token(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
) -> AzureDevOpsUser:
    """
    Valida token de autenticação Azure DevOps.

    Suporta:
    - Bearer token (do Azure DevOps Extension SDK)
    - Basic auth com PAT (para desenvolvimento/testes)

    Quando AUTH_ENABLED=false, retorna usuário mock para desenvolvimento.
    """
    # Modo desenvolvimento sem autenticação
    if not settings.auth_enabled:
        logger.info("Auth desabilitada - retornando usuário mock")
        return AzureDevOpsUser(
            id="dev-user-001",
            display_name="Dev User",
            email="dev@localhost",
            token="mock-token",
        )

    # Verificar se credentials foram fornecidas
    if not credentials:
        logger.warning("Nenhuma credencial fornecida")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de autenticação não fornecido",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials
    logger.debug(f"Token recebido (primeiros 10 chars): {token[:10]}...")

    # Tentar validar como Bearer token ou PAT
    user_info, error_msg = await _fetch_user_profile(token)

    if not user_info:
        logger.error(f"Falha na autenticação: {error_msg}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token inválido ou expirado. Detalhes: {error_msg}",
            headers={"WWW-Authenticate": "Bearer"},
        )

    logger.info(f"Usuário autenticado: {user_info.display_name}")
    return user_info


async def _fetch_user_profile(token: str) -> tuple[AzureDevOpsUser | None, str]:
    """
    Busca perfil do usuário na API do Azure DevOps.
    Tenta validar usando connectionData na organização (se configurada)
    ou no profile global.
    """
    # Determinar URL de validação
    if settings.azure_devops_org_url:
        org_url = settings.azure_devops_org_url.rstrip("/")
        validation_url = f"{org_url}/_apis/connectionData?api-version=7.1-preview.1"
    else:
        validation_url = "https://app.vssps.visualstudio.com/_apis/profile/profiles/me?api-version=7.1-preview.1"

    async with httpx.AsyncClient(timeout=10.0) as client:
        # Tentar primeiro como PAT (Basic Auth)
        pat_encoded = base64.b64encode(f":{token}".encode()).decode()

        try:
            # 1. Tentativa PAT (Basic)
            response = await client.get(
                validation_url, headers={"Authorization": f"Basic {pat_encoded}"}
            )

            if response.status_code == 200:
                data = response.json()
                if "authenticatedUser" in data:
                    user = data["authenticatedUser"]
                    return (
                        AzureDevOpsUser(
                            id=user.get("id", ""),
                            display_name=user.get(
                                "providerDisplayName",
                                user.get("customDisplayName", "Unknown"),
                            ),
                            email=user.get("properties", {})
                            .get("Account", {})
                            .get("$value"),
                            token=token,
                        ),
                        "",
                    )
                else:
                    return (
                        AzureDevOpsUser(
                            id=data.get("id", ""),
                            display_name=data.get("displayName", "Unknown"),
                            email=data.get("emailAddress"),
                            token=token,
                        ),
                        "",
                    )

            # 2. Tentativa Bearer (Azure DevOps Extension SDK)
            response = await client.get(
                validation_url, headers={"Authorization": f"Bearer {token}"}
            )

            if response.status_code == 200:
                data = response.json()
                if "authenticatedUser" in data:
                    user = data["authenticatedUser"]
                    return (
                        AzureDevOpsUser(
                            id=user.get("id", ""),
                            display_name=user.get(
                                "providerDisplayName",
                                user.get("customDisplayName", "Unknown"),
                            ),
                            email=user.get("properties", {})
                            .get("Account", {})
                            .get("$value"),
                            token=token,
                        ),
                        "",
                    )
                else:
                    return (
                        AzureDevOpsUser(
                            id=data.get("id", ""),
                            display_name=data.get("displayName", "Unknown"),
                            email=data.get("emailAddress"),
                            token=token,
                        ),
                        "",
                    )

            # Falha final
            error_body = response.text[:200] if response.text else "Sem corpo"
            logger.warning(
                f"Falha auth na URL {validation_url}: Status {response.status_code}"
            )
            return None, f"Status {response.status_code}: {error_body}"

        except httpx.TimeoutException:
            return None, "Timeout ao conectar com Azure DevOps"
        except Exception as e:
            logger.error(f"Erro na validação do token: {str(e)}")
            return None, f"Erro de conexão: {str(e)}"


def get_current_user(
    user: AzureDevOpsUser = Depends(validate_azure_token),
) -> AzureDevOpsUser:
    """Dependency para obter usuário atual autenticado."""
    return user
