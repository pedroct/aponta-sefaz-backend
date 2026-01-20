"""
Schemas Pydantic para validacao de dados da entidade Apontamento.
"""

import re
from datetime import datetime, date
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict, field_validator, field_serializer
import pytz


class AtividadeSimples(BaseModel):
    """Schema simplificado de atividade para resposta de apontamento."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(..., description="ID unico da atividade")
    nome: str = Field(..., description="Nome da atividade")


class ApontamentoBase(BaseModel):
    """Schema base com campos comuns."""

    data_apontamento: date = Field(
        ...,
        description="Data em que o trabalho foi realizado (formato: YYYY-MM-DD)",
    )
    duracao: str = Field(
        ...,
        min_length=4,
        max_length=5,
        description="Duracao no formato HH:mm (ex: 01:00, 02:30, 08:00). "
        "Atalhos do frontend: +0.5h, +1h, +2h, +4h adicionam ao valor atual.",
    )
    id_atividade: UUID = Field(
        ...,
        description="ID da atividade/tipo de atividade (ex: Documentacao, Desenvolvimento)",
    )
    comentario: str | None = Field(
        default=None,
        max_length=500,
        description="Comentario sobre o trabalho realizado (max 500 caracteres)",
    )

    @field_validator("duracao")
    @classmethod
    def validate_duracao(cls, v: str) -> str:
        """Valida o formato da duracao (HH:mm)."""
        if not v:
            raise ValueError("Duracao e obrigatoria")

        # Aceita formato H:mm ou HH:mm
        pattern = r"^(\d{1,2}):([0-5]\d)$"
        match = re.match(pattern, v)
        if not match:
            raise ValueError(
                "Duracao deve estar no formato HH:mm (ex: 01:00, 02:30, 08:00)"
            )

        horas = int(match.group(1))
        minutos = int(match.group(2))

        # Validar limites razoaveis (max 24 horas)
        if horas > 24:
            raise ValueError("Duracao nao pode exceder 24 horas")

        if horas == 0 and minutos == 0:
            raise ValueError("Duracao deve ser maior que 00:00")

        # Normalizar para formato HH:mm
        return f"{horas:02d}:{minutos:02d}"


class ApontamentoCreate(ApontamentoBase):
    """Schema para criacao de apontamento."""

    # Dados do Azure DevOps (enviados pelo frontend)
    work_item_id: int = Field(
        ...,
        description="ID do Work Item no Azure DevOps (Task ou Bug)",
    )
    project_id: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="ID do projeto no Azure DevOps (IProjectInfo.id). "
        "Pode ser o UUID do projeto (ex: 50a9ca09-710f-4478-8278-2d069902d2af) "
        "ou o nome do projeto (ex: 'Aponta'). Este campo NAO e o ID do banco de dados local.",
    )
    organization_name: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Nome da organizacao no Azure DevOps (IHostContext.name)",
    )

    # Dados do usuario do Azure DevOps
    usuario_id: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="ID do usuario no Azure DevOps (IUserContext.id)",
    )
    usuario_nome: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Nome de exibicao do usuario (IUserContext.displayName)",
    )
    usuario_email: str | None = Field(
        default=None,
        max_length=255,
        description="Email do usuario (IUserContext.name)",
    )


class ApontamentoUpdate(BaseModel):
    """Schema para atualizacao de apontamento (campos opcionais)."""

    data_apontamento: date | None = Field(
        default=None,
        description="Data em que o trabalho foi realizado",
    )
    duracao: str | None = Field(
        default=None,
        min_length=4,
        max_length=5,
        description="Duracao no formato HH:mm (ex: 01:00, 02:30)",
    )
    id_atividade: UUID | None = Field(
        default=None,
        description="ID da atividade associada ao apontamento",
    )
    comentario: str | None = Field(
        default=None,
        max_length=500,
        description="Comentario sobre o trabalho realizado (max 500 caracteres)",
    )

    @field_validator("duracao")
    @classmethod
    def validate_duracao(cls, v: str | None) -> str | None:
        """Valida o formato da duracao (HH:mm) se fornecido."""
        if v is None:
            return None

        pattern = r"^(\d{1,2}):([0-5]\d)$"
        match = re.match(pattern, v)
        if not match:
            raise ValueError(
                "Duracao deve estar no formato HH:mm (ex: 01:00, 02:30, 08:00)"
            )

        horas = int(match.group(1))
        minutos = int(match.group(2))

        if horas > 24:
            raise ValueError("Duracao nao pode exceder 24 horas")

        if horas == 0 and minutos == 0:
            raise ValueError("Duracao deve ser maior que 00:00")

        return f"{horas:02d}:{minutos:02d}"



from pydantic import field_serializer
import pytz

class ApontamentoResponse(BaseModel):
    """Schema de resposta com todos os campos."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(..., description="ID unico do apontamento")
    work_item_id: int = Field(..., description="ID do Work Item no Azure DevOps")
    project_id: str = Field(..., description="ID do projeto no Azure DevOps")
    organization_name: str = Field(..., description="Nome da organizacao no Azure DevOps")
    data_apontamento: date = Field(..., description="Data do apontamento")
    duracao: str = Field(..., description="Duracao no formato HH:mm")
    duracao_horas: float = Field(..., description="Duracao em horas decimais (ex: 1.5 para 01:30)")
    id_atividade: UUID = Field(..., description="ID da atividade")
    atividade: AtividadeSimples = Field(..., description="Dados da atividade")
    comentario: str | None = Field(default=None, description="Comentario")
    usuario_id: str = Field(..., description="ID do usuario")
    usuario_nome: str = Field(..., description="Nome do usuario")
    usuario_email: str | None = Field(default=None, description="Email do usuario")
    criado_em: datetime = Field(..., description="Data de criacao")
    atualizado_em: datetime = Field(..., description="Data da ultima atualizacao")

    @field_serializer("criado_em", "atualizado_em")
    def serialize_datetime(self, value, _info):
        if value is None:
            return None
        utc = pytz.utc
        fortaleza = pytz.timezone("America/Fortaleza")
        if value.tzinfo is None:
            value = utc.localize(value)
        return value.astimezone(fortaleza).isoformat()

    @field_serializer("criado_em", "atualizado_em")
    def serialize_datetime(self, value, _info):
        if value is None:
            return None
        utc = pytz.utc
        fortaleza = pytz.timezone("America/Fortaleza")
        if value.tzinfo is None:
            value = utc.localize(value)
        return value.astimezone(fortaleza).isoformat()


class ApontamentoListResponse(BaseModel):
    """Schema de resposta para listagem de apontamentos."""

    items: list[ApontamentoResponse]
    total: int = Field(..., description="Total de registros")
    total_horas: float = Field(..., description="Total de horas apontadas (decimal)")
    total_formatado: str = Field(..., description="Total formatado como HH:mm")


class ResumoPorAtividade(BaseModel):
    """Resumo por atividade."""

    id: str = Field(..., description="ID da atividade")
    nome: str = Field(..., description="Nome da atividade")
    total_horas: float = Field(..., description="Total de horas")


class ResumoPorUsuario(BaseModel):
    """Resumo por usuário."""

    id: str = Field(..., description="ID do usuário")
    nome: str = Field(..., description="Nome do usuário")
    total_horas: float = Field(..., description="Total de horas")


class ApontamentoResumo(BaseModel):
    """Schema para resumo de apontamentos de um work item."""

    work_item_id: int = Field(..., description="ID do Work Item")
    total_horas: float = Field(..., description="Total de horas apontadas (decimal)")
    total_apontamentos: int = Field(..., description="Quantidade de apontamentos")
    media_horas_por_apontamento: float = Field(
        ..., description="Média de horas por apontamento"
    )
    primeira_data: date | None = Field(
        default=None, description="Primeira data registrada"
    )
    ultima_data: date | None = Field(
        default=None, description="Última data registrada"
    )
    por_atividade: list[ResumoPorAtividade] = Field(
        default_factory=list, description="Totais por atividade"
    )
    por_usuario: list[ResumoPorUsuario] = Field(
        default_factory=list, description="Totais por usuário"
    )
