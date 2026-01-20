"""
Endpoints de usuário autenticado.
"""

from fastapi import APIRouter, Depends
from app.auth import get_current_user, AzureDevOpsUser
from app.schemas.user import UserResponse

router = APIRouter(prefix="/user", tags=["User"])


@router.get("", response_model=UserResponse, summary="Usuário atual")
def get_user(current_user: AzureDevOpsUser = Depends(get_current_user)) -> UserResponse:
    """Retorna o usuário autenticado no Azure DevOps."""
    return UserResponse(
        id=current_user.id,
        displayName=current_user.display_name,
        emailAddress=current_user.email,
        avatarUrl=current_user.avatar_url,
    )
