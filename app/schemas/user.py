"""
Schema de resposta para usuário autenticado.
"""

from pydantic import BaseModel, Field


class UserResponse(BaseModel):
    """Schema de resposta de usuário para o frontend."""

    id: str = Field(..., description="ID do usuário no Azure DevOps")
    displayName: str = Field(..., description="Nome de exibição do usuário")
    emailAddress: str | None = Field(
        default=None, description="Email do usuário"
    )
    avatarUrl: str | None = Field(
        default=None, description="URL do avatar do usuário"
    )
