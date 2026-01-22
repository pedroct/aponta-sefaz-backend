"""
Schemas Pydantic para o Timesheet (Folha de Horas).
Define a estrutura hierárquica de Work Items com apontamentos agregados por semana.
"""

from datetime import date
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict


class ApontamentoDia(BaseModel):
    """Apontamento resumido para uma célula do timesheet."""

    id: UUID = Field(..., description="ID único do apontamento")
    duracao: str = Field(..., description="Duração no formato HH:mm")
    duracao_horas: float = Field(..., description="Duração em horas decimais")
    id_atividade: UUID = Field(..., description="ID da atividade")
    atividade_nome: str = Field(..., description="Nome da atividade")
    comentario: str | None = Field(default=None, description="Comentário")


class CelulaDia(BaseModel):
    """Representa uma célula de dia no timesheet."""

    data: date = Field(..., description="Data do dia")
    dia_semana: str = Field(..., description="Nome abreviado do dia (seg, ter, etc)")
    dia_numero: int = Field(..., description="Número do dia no mês")
    total_horas: float = Field(default=0.0, description="Total de horas do dia")
    total_formatado: str = Field(default="", description="Total formatado HH:mm")
    apontamentos: list[ApontamentoDia] = Field(
        default_factory=list, description="Lista de apontamentos do dia"
    )
    eh_hoje: bool = Field(default=False, description="Se é o dia atual")
    eh_fim_semana: bool = Field(default=False, description="Se é sábado ou domingo")


class WorkItemTimesheet(BaseModel):
    """Work Item com dados para o timesheet."""

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., description="ID do Work Item no Azure DevOps")
    title: str = Field(..., description="Título do Work Item")
    type: str = Field(..., description="Tipo do Work Item (Epic, Feature, etc)")
    state: str = Field(..., description="Estado atual do Work Item")
    state_category: str = Field(
        default="InProgress",
        description="Categoria do estado (Proposed, InProgress, Resolved, Completed, Removed)",
    )
    icon_url: str = Field(default="", description="URL do ícone do tipo")
    assigned_to: str | None = Field(default=None, description="Usuário atribuído")

    # Campos de esforço do Azure DevOps
    original_estimate: float | None = Field(
        default=None, description="Estimativa original (horas) - Coluna E (Estimado)"
    )
    completed_work: float | None = Field(
        default=None, description="Trabalho completado (horas) - calculado pelos apontamentos"
    )
    remaining_work: float | None = Field(
        default=None, description="Trabalho restante (horas) - Coluna S (Saldo) - OriginalEstimate - CompletedWork"
    )

    # Totais da semana (apontamentos locais)
    total_semana_horas: float = Field(
        default=0.0, description="Total de horas apontadas na semana - Coluna H (Histórico)"
    )
    total_semana_formatado: str = Field(
        default="", description="Total da semana formatado HH:mm"
    )

    # Células dos dias da semana (seg a dom)
    dias: list[CelulaDia] = Field(
        default_factory=list, description="Células dos 7 dias da semana"
    )

    # Hierarquia
    nivel: int = Field(default=0, description="Nível na hierarquia (0=Epic, 1=Feature, etc)")
    parent_id: int | None = Field(default=None, description="ID do Work Item pai")
    children: list["WorkItemTimesheet"] = Field(
        default_factory=list, description="Work Items filhos"
    )

    # Flags de permissão
    pode_editar: bool = Field(
        default=True,
        description="Se permite edição (baseado na categoria do estado)",
    )
    pode_excluir: bool = Field(
        default=True,
        description="Se permite exclusão (baseado na categoria do estado)",
    )


class TotalDia(BaseModel):
    """Total de horas para um dia na linha de totais."""

    data: date = Field(..., description="Data do dia")
    dia_semana: str = Field(..., description="Nome abreviado do dia")
    dia_numero: int = Field(..., description="Número do dia")
    total_horas: float = Field(default=0.0, description="Total de horas")
    total_formatado: str = Field(default="", description="Total formatado HH:mm")
    eh_hoje: bool = Field(default=False, description="Se é o dia atual")


class TimesheetResponse(BaseModel):
    """Resposta completa do timesheet para uma semana."""

    # Período
    semana_inicio: date = Field(..., description="Data de início da semana (segunda)")
    semana_fim: date = Field(..., description="Data de fim da semana (domingo)")
    semana_label: str = Field(..., description="Label da semana (ex: '19/01 - 25/01')")

    # Hierarquia de Work Items
    work_items: list[WorkItemTimesheet] = Field(
        default_factory=list, description="Árvore hierárquica de Work Items"
    )

    # Totais gerais
    total_geral_horas: float = Field(
        default=0.0, description="Total geral de horas da semana"
    )
    total_geral_formatado: str = Field(
        default="", description="Total geral formatado HH:mm"
    )
    totais_por_dia: list[TotalDia] = Field(
        default_factory=list, description="Totais por dia da semana"
    )

    # Metadados
    total_work_items: int = Field(
        default=0, description="Total de Work Items listados"
    )

    # Colunas E e H agregadas
    total_esforco: float = Field(
        default=0.0, description="Soma total da coluna E (Esforço)"
    )
    total_historico: float = Field(
        default=0.0, description="Soma total da coluna H (Histórico)"
    )


class TimesheetQueryParams(BaseModel):
    """Parâmetros de consulta para o timesheet."""

    week_start: date | None = Field(
        default=None,
        description="Data de início da semana (segunda). Se não informado, usa a semana atual.",
    )
    project_id: str = Field(
        ...,
        description="ID do projeto no Azure DevOps",
    )
    organization_name: str = Field(
        ...,
        description="Nome da organização no Azure DevOps",
    )
    only_my_items: bool = Field(
        default=False,
        description="Filtrar apenas itens atribuídos ao usuário logado",
    )
    current_project_only: bool = Field(
        default=True,
        description="Filtrar apenas itens do projeto atual",
    )


class StateCategory(BaseModel):
    """Categoria de estado de um Work Item."""

    state: str = Field(..., description="Nome do estado")
    category: str = Field(
        ...,
        description="Categoria do estado (Proposed, InProgress, Resolved, Completed, Removed)",
    )
    can_edit: bool = Field(
        ...,
        description="Se permite edição de apontamentos",
    )
    can_delete: bool = Field(
        ...,
        description="Se permite exclusão de apontamentos",
    )


class StateCategoryResponse(BaseModel):
    """Resposta com a categoria de estado de um Work Item."""

    work_item_id: int = Field(..., description="ID do Work Item")
    state: str = Field(..., description="Estado atual")
    state_category: str = Field(..., description="Categoria do estado")
    can_edit: bool = Field(..., description="Permite edição")
    can_delete: bool = Field(..., description="Permite exclusão")


class WorkItemRevisionFields(BaseModel):
    """Campos de uma revisão de Work Item."""

    changed_date: str = Field(..., alias="System.ChangedDate")
    state: str | None = Field(None, alias="System.State")
    assigned_to: dict | None = Field(None, alias="System.AssignedTo")

    class Config:
        populate_by_name = True


class WorkItemRevision(BaseModel):
    """Uma revisão de um Work Item."""

    rev: int = Field(..., description="Número da revisão")
    fields: WorkItemRevisionFields


class WorkItemRevisionsResponse(BaseModel):
    """Resposta com o histórico de revisões de um Work Item."""

    work_item_id: int = Field(..., description="ID do Work Item")
    revisions: list[WorkItemRevision] = Field(..., description="Lista de revisões")


class ProcessStateMapping(BaseModel):
    """Mapeamento de estados para categorias de um processo."""

    state_map: dict[str, str] = Field(
        ..., 
        description="Dicionário mapeando nome do estado -> categoria (ex: {'Active': 'InProgress'})"
    )


class WorkItemCurrentState(BaseModel):
    """Estado atual de um Work Item."""

    id: int = Field(..., description="ID do Work Item")
    state: str | None = Field(None, description="Estado atual")
    type: str | None = Field(None, description="Tipo do Work Item")
    assigned_to: dict | None = Field(None, description="Usuário atribuído")


class WorkItemsCurrentStateResponse(BaseModel):
    """Resposta com o estado atual de múltiplos Work Items."""

    work_items: dict[int, WorkItemCurrentState] = Field(
        ...,
        description="Dicionário mapeando work_item_id -> estado atual"
    )
