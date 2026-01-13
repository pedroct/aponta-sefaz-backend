"""
Schemas Pydantic para validação de dados da entidade Atividade.
"""

from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict


class AtividadeBase(BaseModel):
    """Schema base com campos comuns."""

    nome: str = Field(
        ..., min_length=1, max_length=255, description="Nome da atividade"
    )
    descricao: str | None = Field(
        default=None, description="Descrição detalhada da atividade"
    )
    ativo: bool = Field(default=True, description="Status ativo/inativo da atividade")
    id_projeto: UUID = Field(..., description="ID do projeto associado")


class AtividadeCreate(AtividadeBase):
    """Schema para criação de atividade."""

    pass


class AtividadeUpdate(BaseModel):
    """Schema para atualização de atividade (campos opcionais)."""

    nome: str | None = Field(
        default=None, min_length=1, max_length=255, description="Nome da atividade"
    )
    descricao: str | None = Field(
        default=None, description="Descrição detalhada da atividade"
    )
    ativo: bool | None = Field(
        default=None, description="Status ativo/inativo da atividade"
    )
    id_projeto: UUID | None = Field(default=None, description="ID do projeto associado")


class AtividadeResponse(AtividadeBase):
    """Schema de resposta com todos os campos."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(..., description="ID único da atividade")
    criado_por: str | None = Field(
        default=None, description="Email ou ID do usuário que criou a atividade"
    )
    criado_em: datetime = Field(..., description="Data de criação")
    atualizado_em: datetime = Field(..., description="Data da última atualização")
    nome_projeto: str | None = Field(
        default=None, description="Nome do projeto associado"
    )


class AtividadeListResponse(BaseModel):
    """Schema de resposta para listagem."""

    items: list[AtividadeResponse]
    total: int = Field(..., description="Total de registros")
