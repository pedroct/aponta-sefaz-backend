"""
Schemas Pydantic para a entidade Projeto.
"""

from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict


class ProjetoResponse(BaseModel):
    """Schema de resposta de projeto."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(..., description="ID interno do projeto")
    external_id: UUID = Field(..., description="ID do projeto no Azure DevOps")
    nome: str = Field(..., description="Nome do projeto")
    descricao: str | None = Field(default=None, description="Descrição do projeto")
    url: str | None = Field(default=None, description="URL do projeto no Azure DevOps")
    estado: str | None = Field(default=None, description="Estado do projeto")
    last_sync_at: datetime | None = Field(
        default=None, description="Data da última sincronização"
    )
    created_at: datetime | None = Field(default=None, description="Data de criação")
    updated_at: datetime | None = Field(default=None, description="Data de atualização")
