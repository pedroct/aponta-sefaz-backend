"""
Schemas Pydantic para validação de dados da entidade Atividade.
"""

from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict, field_validator


class ProjetoSimples(BaseModel):
    """Schema simplificado de projeto para resposta de atividade."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(..., description="ID único do projeto")
    nome: str = Field(..., description="Nome do projeto")


class AtividadeBase(BaseModel):
    """Schema base com campos comuns."""

    nome: str = Field(
        ..., min_length=1, max_length=255, description="Nome da atividade"
    )
    descricao: str | None = Field(
        default=None, description="Descrição detalhada da atividade"
    )
    ativo: bool = Field(default=True, description="Status ativo/inativo da atividade")


class AtividadeCreate(AtividadeBase):
    """Schema para criação de atividade."""

    ids_projetos: list[UUID] = Field(
        ...,
        min_length=1,
        description="Lista de IDs dos projetos associados (mínimo 1)",
    )

    # Retrocompatibilidade: aceita id_projeto (singular) e converte para ids_projetos
    id_projeto: UUID | None = Field(
        default=None,
        description="ID do projeto associado (retrocompatibilidade - use ids_projetos)",
        exclude=True,
    )

    @field_validator("ids_projetos", mode="before")
    @classmethod
    def ensure_list(cls, v, info):
        """Garante que ids_projetos seja uma lista."""
        if v is None:
            # Se ids_projetos não foi fornecido, tenta usar id_projeto
            id_projeto = info.data.get("id_projeto")
            if id_projeto:
                return [id_projeto]
            return v
        return v


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
    ids_projetos: list[UUID] | None = Field(
        default=None,
        min_length=1,
        description="Lista de IDs dos projetos associados (substitui todos os existentes)",
    )

    # Retrocompatibilidade: aceita id_projeto (singular)
    id_projeto: UUID | None = Field(
        default=None,
        description="ID do projeto associado (retrocompatibilidade - use ids_projetos)",
        exclude=True,
    )


class AtividadeResponse(AtividadeBase):
    """Schema de resposta com todos os campos."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(..., description="ID único da atividade")
    projetos: list[ProjetoSimples] = Field(
        default_factory=list, description="Lista de projetos associados"
    )
    criado_por: str | None = Field(
        default=None, description="Email ou ID do usuário que criou a atividade"
    )
    criado_em: datetime = Field(..., description="Data de criação")
    atualizado_em: datetime = Field(..., description="Data da última atualização")

    # Campos de retrocompatibilidade
    id_projeto: UUID | None = Field(
        default=None, description="ID do primeiro projeto (retrocompatibilidade)"
    )
    nome_projeto: str | None = Field(
        default=None, description="Nome do primeiro projeto (retrocompatibilidade)"
    )


class AtividadeListResponse(BaseModel):
    """Schema de resposta para listagem."""

    items: list[AtividadeResponse]
    total: int = Field(..., description="Total de registros")
