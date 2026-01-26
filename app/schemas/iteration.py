"""
Schemas Pydantic para Iterations (Sprints) do Azure DevOps.
Define a estrutura de dados para listar e filtrar iterations.
"""

from datetime import datetime
from pydantic import BaseModel, Field


class IterationAttributes(BaseModel):
    """Atributos de uma Iteration."""

    start_date: datetime | None = Field(
        default=None,
        alias="startDate",
        description="Data de início da iteration"
    )
    finish_date: datetime | None = Field(
        default=None,
        alias="finishDate",
        description="Data de fim da iteration"
    )
    time_frame: str | None = Field(
        default=None,
        alias="timeFrame",
        description="Período da iteration: past, current, future"
    )

    class Config:
        populate_by_name = True


class IterationResponse(BaseModel):
    """Resposta de uma Iteration do Azure DevOps."""

    id: str = Field(..., description="ID único da iteration (UUID)")
    name: str = Field(..., description="Nome da iteration (ex: 'Sprint 5')")
    path: str | None = Field(
        default=None,
        description="Caminho completo (ex: 'Project\\Iteration\\Sprint 5')"
    )
    attributes: IterationAttributes = Field(
        default_factory=IterationAttributes,
        description="Atributos da iteration (datas e timeFrame)"
    )
    url: str | None = Field(default=None, description="URL da API da iteration")

    class Config:
        populate_by_name = True


class IterationsListResponse(BaseModel):
    """Resposta com lista de Iterations."""

    count: int = Field(..., description="Quantidade de iterations retornadas")
    iterations: list[IterationResponse] = Field(
        default_factory=list,
        description="Lista de iterations"
    )
    current_iteration_id: str | None = Field(
        default=None,
        description="ID da iteration atual (timeFrame=current) para pré-seleção"
    )


class IterationWorkItemsResponse(BaseModel):
    """Resposta com IDs dos Work Items de uma Iteration."""

    iteration_id: str = Field(..., description="ID da iteration")
    iteration_name: str = Field(..., description="Nome da iteration")
    work_item_ids: list[int] = Field(
        default_factory=list,
        description="Lista de IDs dos Work Items na iteration"
    )
    count: int = Field(default=0, description="Quantidade de Work Items")
