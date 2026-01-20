"""
Schemas para busca de Work Items no Azure DevOps.
"""

from pydantic import BaseModel, Field


class WorkItem(BaseModel):
    """Representação de um work item retornado na busca."""

    id: int = Field(..., description="ID do work item")
    title: str = Field(..., description="Título do work item")
    type: str = Field(..., description="Tipo do work item (Feature, Bug, Task, etc.)")
    project: str = Field(..., description="Projeto do work item")
    url: str = Field(..., description="URL do work item no Azure DevOps")
    iconUrl: str = Field(
        ...,
        description="Data URI SVG do ícone do tipo de work item"
    )
    originalEstimate: float | None = Field(
        default=None, description="Estimativa original (horas)"
    )
    completedWork: float | None = Field(
        default=None, description="Trabalho completado (horas)"
    )
    remainingWork: float | None = Field(
        default=None, description="Trabalho restante (horas)"
    )
    state: str = Field(..., description="Estado do work item")


class WorkItemSearchResponse(BaseModel):
    """Resposta da busca de work items."""

    results: list[WorkItem]
    count: int = Field(..., description="Quantidade total de itens retornados")
