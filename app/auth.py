"""
Módulo de autenticação Azure DevOps.
Suporta autenticação via:
- Personal Access Token (PAT) para desenvolvimento
- Bearer OAuth Token (do SDK Azure DevOps) para produção em iframe
"""

import base64
import json
import logging
import httpx
import re
from fastapi import Depends, HTTPException, Request, status
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
        avatar_url: str | None = None,
    ):
        self.id = id
        self.display_name = display_name
        self.email = email
        self.token = token
        self.avatar_url = avatar_url

    def __repr__(self) -> str:
        return f"<AzureDevOpsUser(id={self.id}, name='{self.display_name}')>"


async def validate_azure_token(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
) -> AzureDevOpsUser:
    """
    Valida token de autenticação Azure DevOps.

    Suporta:
    - Basic auth com PAT (para desenvolvimento/testes)

    Quando AUTH_ENABLED=false, retorna usuário mock para desenvolvimento.
    """
    # Modo desenvolvimento sem autenticação
    if not settings.auth_enabled:
        logger.info("Auth desabilitada - tentando obter usuário via PAT")
        dev_token = settings.azure_devops_pat or ""
        if dev_token:
            user_info, _ = await _fetch_user_profile(dev_token)
            if user_info:
                _apply_custom_header_user_info(user_info, request)
                return user_info

        logger.info("Auth desabilitada - retornando usuário mock")
        return AzureDevOpsUser(
            id="dev-user-001",
            display_name="Dev User",
            email="dev@localhost",
            token=dev_token,
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

    # 0. Verificar se é um JWT (App Token da extensão)
    if token.count(".") == 2 and (token.startswith("eyJ") or token.startswith("eyK")):
        try:
            # Decodificar payload sem verificar assinatura (Server-to-Server trust implícito por enquanto)
            parts = token.split(".")
            payload_b64 = parts[1] + "=" * (4 - len(parts[1]) % 4)
            payload_json = base64.urlsafe_b64decode(payload_b64).decode()
            claims = json.loads(payload_json)

            if "app.vstoken" in claims.get("iss", ""):
                user_id = claims.get("nameid")
                display_name = claims.get("name", f"Azure User {user_id[:8]}")
                logger.info(f"App Token detectado para usuário {user_id}")
                return AzureDevOpsUser(
                    id=user_id,
                    display_name=display_name,
                    email=claims.get("email"),
                    token=token,
                )
        except Exception:
            pass

    scheme = credentials.scheme.lower()  # 'bearer' ou 'basic'
    logger.debug(f"Token recebido (scheme={scheme}, primeiros 10 chars): {token[:10]}...")

    # Detectar tipo de autenticação:
    # - Bearer: Token OAuth do SDK Azure DevOps (produção/iframe)
    # - Basic: PAT codificado em base64 (desenvolvimento)
    # - Bearer com PAT: Também suportado para flexibilidade
    is_bearer = scheme == "bearer"
    
    # Validar token (Bearer OAuth ou PAT)
    user_info, error_msg = await _fetch_user_profile(token, is_bearer=is_bearer)

    if not user_info:
        logger.error(f"Falha na autenticação: {error_msg}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token inválido ou expirado. Detalhes: {error_msg}",
            headers={"WWW-Authenticate": "Bearer"},
        )

    logger.info(f"Usuário autenticado: {user_info.display_name}")
    _apply_custom_header_user_info(user_info, request)
    return user_info


async def _fetch_user_profile(
    token: str, is_bearer: bool = False
) -> tuple[AzureDevOpsUser | None, str]:
    """
    Busca perfil do usuário na API do Azure DevOps.
    
    Args:
        token: Token de autenticação (PAT ou Bearer OAuth)
        is_bearer: Se True, usa Bearer auth (OAuth do SDK).
                   Se False, usa Basic auth (PAT).
    
    Para tokens OAuth (Bearer):
    - Usa o endpoint global de profile: app.vssps.visualstudio.com
    - Não segue redirects (302 = token inválido)
    
    Para PAT (Basic):
    - Usa connectionData na organização se configurada
    - Segue redirects normalmente
    """
    # Determinar URL de validação baseado no tipo de token
    if is_bearer:
        # Token OAuth do SDK - SEMPRE usa endpoint global de profile
        # Este é o endpoint correto para validar tokens OAuth do Azure DevOps Extension SDK
        validation_url = "https://app.vssps.visualstudio.com/_apis/profile/profiles/me?api-version=7.0"
        logger.debug(f"OAuth token: usando endpoint global {validation_url}")
    elif settings.azure_devops_org_url:
        # PAT - usa connectionData na organização
        org_url = settings.azure_devops_org_url.rstrip("/")
        validation_url = f"{org_url}/_apis/connectionData?api-version=7.1-preview.1"
    else:
        # PAT sem org configurada - usa profile global
        validation_url = "https://app.vssps.visualstudio.com/_apis/profile/profiles/me?api-version=7.0"

    profile_url = _build_profile_url(settings.azure_devops_org_url)

    # Para OAuth, não seguir redirects (302 = token inválido)
    # Para PAT, seguir redirects normalmente
    async with httpx.AsyncClient(timeout=15.0, follow_redirects=not is_bearer) as client:
        # Montar header de autorização baseado no tipo de token
        if is_bearer:
            # Bearer OAuth (token do SDK Azure DevOps)
            auth_header = f"Bearer {token}"
            logger.debug(f"Usando Bearer OAuth para autenticação (token length: {len(token)})")
        else:
            # Basic Auth com PAT
            pat_encoded = base64.b64encode(f":{token}".encode()).decode()
            auth_header = f"Basic {pat_encoded}"
            logger.debug(f"Usando Basic Auth (PAT) para autenticação (token length: {len(token)})")

        try:
            # Validar token
            logger.debug(f"Fazendo requisição para: {validation_url}")
            response = await client.get(
                validation_url, headers={"Authorization": auth_header}
            )
            
            logger.debug(f"Response status: {response.status_code}")
            
            # Para OAuth, 302 significa token inválido (redirect para login)
            if is_bearer and response.status_code in (301, 302, 303, 307, 308):
                logger.warning(f"OAuth token inválido: recebido redirect {response.status_code}")
                return None, f"Token OAuth inválido ou expirado (redirect {response.status_code})"

            if response.status_code == 200:
                data = response.json()
                
                # Buscar dados completos do profile (displayName, email, avatar)
                profile_data = await _fetch_profile_data(
                    client, token, profile_url, is_bearer=is_bearer
                )
                
                # Converter avatar base64 para data URL se existir
                avatar_url = None
                if profile_data and profile_data.avatar_base64:
                    avatar_url = f"data:image/png;base64,{profile_data.avatar_base64}"
                
                if "authenticatedUser" in data:
                    user = data["authenticatedUser"]
                    display_name = user.get(
                        "providerDisplayName",
                        user.get("customDisplayName", "Unknown"),
                    )
                    
                    # Usar dados do profile se disponíveis
                    if profile_data and profile_data.display_name:
                        display_name = profile_data.display_name
                    elif display_name:
                        display_name = _maybe_normalize_display_name(
                            display_name,
                            user.get("properties", {})
                            .get("Account", {})
                            .get("$value"),
                        )
                    
                    email = user.get("properties", {}).get("Account", {}).get("$value")
                    if profile_data and profile_data.email:
                        email = profile_data.email
                        
                    return (
                        AzureDevOpsUser(
                            id=user.get("id", ""),
                            display_name=display_name,
                            email=email,
                            token=token,
                            avatar_url=avatar_url,
                        ),
                        "",
                    )
                else:
                    display_name = data.get("displayName", "Unknown")
                    
                    # Usar dados do profile se disponíveis
                    if profile_data and profile_data.display_name:
                        display_name = profile_data.display_name
                    elif display_name:
                        display_name = _maybe_normalize_display_name(
                            display_name,
                            data.get("emailAddress"),
                        )
                    
                    email = data.get("emailAddress")
                    if profile_data and profile_data.email:
                        email = profile_data.email
                        
                    return (
                        AzureDevOpsUser(
                            id=data.get("id", ""),
                            display_name=display_name,
                            email=email,
                            token=token,
                            avatar_url=avatar_url,
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


def _build_profile_url(org_url: str | None) -> str:
    """Monta a URL do Profile API para obter o displayName completo."""
    if not org_url:
        return "https://app.vssps.visualstudio.com/_apis/profile/profiles/me?api-version=7.1-preview.1"

    match = re.search(r"dev\.azure\.com/([^/]+)", org_url)
    if match:
        org = match.group(1)
        return f"https://vssps.dev.azure.com/{org}/_apis/profile/profiles/me?api-version=7.1-preview.1"

    return "https://app.vssps.visualstudio.com/_apis/profile/profiles/me?api-version=7.1-preview.1"


def _apply_custom_header_user_info(
    user_info: AzureDevOpsUser, request: Request | None
) -> None:
    """Sobrescreve displayName/email com dados do header x-custom-header (base64 JSON)."""
    if not request:
        return

    raw_header = request.headers.get("x-custom-header")
    if not raw_header:
        return

    try:
        decoded = base64.b64decode(raw_header).decode("utf-8")
        payload = json.loads(decoded)
    except Exception:
        return

    full_name = payload.get("User-Name")
    if full_name:
        user_info.display_name = full_name

    email = payload.get("User-Email")
    if email and not user_info.email:
        user_info.email = email


def _maybe_normalize_display_name(display_name: str, email: str | None) -> str:
    """Normaliza displayName usando o email quando o nome parece um identificador curto."""
    if not email:
        return display_name

    has_space = " " in display_name
    looks_like_code = display_name.isalnum() and len(display_name) <= 12
    if has_space or not looks_like_code:
        return display_name

    local_part = email.split("@", 1)[0].strip()
    if not local_part:
        return display_name

    normalized = (
        local_part.replace(".", " ")
        .replace("_", " ")
        .replace("-", " ")
    )
    normalized = " ".join(segment.capitalize() for segment in normalized.split())
    return normalized or display_name


class ProfileData:
    """Dados do perfil obtidos da API Profile do Azure DevOps."""
    def __init__(
        self,
        display_name: str | None = None,
        email: str | None = None,
        avatar_base64: str | None = None,
    ):
        self.display_name = display_name
        self.email = email
        self.avatar_base64 = avatar_base64


async def _fetch_profile_data(
    client: httpx.AsyncClient, token: str, profile_url: str, is_bearer: bool = False
) -> ProfileData | None:
    """
    Obtém dados completos do perfil via Profile API do Azure DevOps.
    
    Extrai de coreAttributes:
    - DisplayName: Nome completo do usuário
    - EmailAddress: Email do usuário
    - Avatar: Imagem em base64
    """
    if not profile_url:
        return None

    # Montar header de autorização baseado no tipo de token
    if is_bearer:
        auth_header = f"Bearer {token}"
    else:
        pat_encoded = base64.b64encode(f":{token}".encode()).decode()
        auth_header = f"Basic {pat_encoded}"

    try:
        response = await client.get(
            profile_url, headers={"Authorization": auth_header}
        )
        if response.status_code == 200:
            data = response.json()
            
            # Tentar extrair de coreAttributes (formato mais completo)
            core_attrs = data.get("coreAttributes", {})
            
            # DisplayName
            display_name = None
            if "DisplayName" in core_attrs:
                display_name = core_attrs["DisplayName"].get("value")
            if not display_name:
                display_name = data.get("displayName")
            
            # EmailAddress
            email = None
            if "EmailAddress" in core_attrs:
                email = core_attrs["EmailAddress"].get("value")
            if not email:
                email = data.get("emailAddress")
            
            # Avatar (base64)
            avatar_base64 = None
            if "Avatar" in core_attrs:
                avatar_data = core_attrs["Avatar"].get("value")
                if isinstance(avatar_data, dict):
                    avatar_base64 = avatar_data.get("value")
                elif isinstance(avatar_data, str):
                    avatar_base64 = avatar_data
            
            if display_name or email or avatar_base64:
                logger.debug(f"Profile obtido: name={display_name}, email={email}, avatar={'sim' if avatar_base64 else 'não'}")
                return ProfileData(
                    display_name=display_name,
                    email=email,
                    avatar_base64=avatar_base64,
                )
                
    except httpx.TimeoutException:
        logger.warning("Timeout ao buscar profile")
        return None
    except Exception as e:
        logger.warning(f"Erro ao buscar profile: {e}")
        return None

    return None


async def _fetch_profile_display_name(
    client: httpx.AsyncClient, token: str, profile_url: str, is_bearer: bool = False
) -> str | None:
    """Tenta obter displayName completo via Profile API (compatibilidade)."""
    profile_data = await _fetch_profile_data(client, token, profile_url, is_bearer)
    return profile_data.display_name if profile_data else None


def get_current_user(
    user: AzureDevOpsUser = Depends(validate_azure_token)  # noqa: B008,
) -> AzureDevOpsUser:
    """Dependency para obter usuário atual autenticado."""
    return user
