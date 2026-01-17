"""
Schemas Pydantic para validação de dados da entidade Apontamento.
"""

from datetime import datetime, date
from uuid import UUID
from typing import Literal
from pydantic import BaseModel, Field, ConfigDict, field_validator


class AtividadeSimples(BaseModel):
    """Schema simplificado de atividade para resposta de apontamento."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(..., description="ID único da atividade")
    nome: str = Field(..., description="Nome da atividade")


class ApontamentoBase(BaseModel):
    """Schema base com campos comuns."""

    data_apontamento: date = Field(
        ...,
        description="Data em que o trabalho foi realizado (formato: YYYY-MM-DD)",
    )
    horas: Literal[0, 1, 2, 3, 4, 5, 6, 7, 8] = Field(
        ...,
        description="Quantidade de horas trabalhadas (0-8)",
    )
    minutos: Literal[0, 15, 30, 45] = Field(
        ...,
        description="Quantidade de minutos trabalhados (0, 15, 30, 45)",
    )
    id_atividade: UUID = Field(
        ...,
        description="ID da atividade associada ao apontamento",
    )
    comentario: str | None = Field(
        default=None,
        max_length=100,
        description="Comentário sobre o trabalho realizado (máx 100 caracteres)",
    )

    @field_validator("horas", "minutos", mode="before")
    @classmethod
    def validate_time_fields(cls, v):
        """Garante que os campos de tempo sejam inteiros."""
        if isinstance(v, str):
            return int(v)
        return v


class ApontamentoCreate(ApontamentoBase):
    """Schema para criação de apontamento."""

    # Dados do Azure DevOps (enviados pelo frontend)
    work_item_id: int = Field(
        ...,
        description="ID do Work Item no Azure DevOps",
    )
    project_id: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="ID do projeto no Azure DevOps (IProjectInfo.id). "
        "Pode ser o UUID do projeto (ex: 50a9ca09-710f-4478-8278-2d069902d2af) "
        "ou o nome do projeto (ex: 'Aponta'). Este campo NÃO é o ID do banco de dados local.",
    )
    organization_name: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Nome da organização no Azure DevOps (IHostContext.name)",
    )

    # Dados do usuário do Azure DevOps
    usuario_id: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="ID do usuário no Azure DevOps (IUserContext.id)",
    )
    usuario_nome: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Nome de exibição do usuário (IUserContext.displayName)",
    )
    usuario_email: str | None = Field(
        default=None,
        max_length=255,
        description="Nome de login do usuário (IUserContext.name)",
    )


class ApontamentoUpdate(BaseModel):
    """Schema para atualização de apontamento (campos opcionais)."""

    data_apontamento: date | None = Field(
        default=None,
        description="Data em que o trabalho foi realizado",
    )
    horas: Literal[0, 1, 2, 3, 4, 5, 6, 7, 8] | None = Field(
        default=None,
        description="Quantidade de horas trabalhadas (0-8)",
    )
    minutos: Literal[0, 15, 30, 45] | None = Field(
        default=None,
        description="Quantidade de minutos trabalhados (0, 15, 30, 45)",
    )
    id_atividade: UUID | None = Field(
        default=None,
        description="ID da atividade associada ao apontamento",
    )
    comentario: str | None = Field(
        default=None,
        max_length=100,
        description="Comentário sobre o trabalho realizado (máx 100 caracteres)",
    )


class ApontamentoResponse(BaseModel):
    """Schema de resposta com todos os campos."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(..., description="ID único do apontamento")
    work_item_id: int = Field(..., description="ID do Work Item no Azure DevOps")
    project_id: str = Field(..., description="ID do projeto no Azure DevOps")
    organization_name: str = Field(..., description="Nome da organização no Azure DevOps")
    data_apontamento: date = Field(..., description="Data do apontamento")
    horas: int = Field(..., description="Horas trabalhadas")
    minutos: int = Field(..., description="Minutos trabalhados")
    tempo_formatado: str = Field(..., description="Tempo formatado como HH:MM")
    id_atividade: UUID = Field(..., description="ID da atividade")
    atividade: AtividadeSimples = Field(..., description="Dados da atividade")
    comentario: str | None = Field(default=None, description="Comentário")
    usuario_id: str = Field(..., description="ID do usuário")
    usuario_nome: str = Field(..., description="Nome do usuário")
    usuario_email: str | None = Field(default=None, description="Email do usuário")
    criado_em: datetime = Field(..., description="Data de criação")
    atualizado_em: datetime = Field(..., description="Data da última atualização")


class ApontamentoListResponse(BaseModel):
    """Schema de resposta para listagem de apontamentos."""

    items: list[ApontamentoResponse]
    total: int = Field(..., description="Total de registros")
    total_horas: int = Field(..., description="Total de horas apontadas")
    total_minutos: int = Field(..., description="Total de minutos apontados")


class ApontamentoResumo(BaseModel):
    """Schema para resumo de apontamentos de um work item."""

    work_item_id: int = Field(..., description="ID do Work Item")
    total_apontamentos: int = Field(..., description="Quantidade de apontamentos")
    total_horas: int = Field(..., description="Total de horas apontadas")
    total_minutos: int = Field(..., description="Total de minutos apontados")
    tempo_total_formatado: str = Field(..., description="Tempo total formatado (HH:MM)")
