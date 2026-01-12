from fastapi import APIRouter, Depends, HTTPException, status
from app.auth import get_current_user, AzureDevOpsUser
from app.services.azure import AzureService

router = APIRouter(prefix="/integracao", tags=["Integração"])


@router.get("/projetos", summary="Listar projetos do Azure DevOps")
async def listar_projetos(current_user: AzureDevOpsUser = Depends(get_current_user)):
    """
    Lista projetos da organização configurada usando o token do usuário autenticado.
    Serve para testar a integração e o escopo do token.
    """
    if not current_user.token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de acesso não disponível para este usuário.",
        )

    service = AzureService(token=current_user.token)
    return await service.list_projects()
