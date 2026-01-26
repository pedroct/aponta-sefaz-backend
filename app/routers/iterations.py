"""
Endpoints REST para Iterations (Sprints) do Azure DevOps.
Permite listar iterations e obter work items de uma iteration específica.
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.auth import AzureDevOpsUser, get_current_user
from app.database import get_db
from app.schemas.iteration import (
    IterationsListResponse,
    IterationWorkItemsResponse,
)
from app.services.iteration_service import IterationService

router = APIRouter(prefix="/iterations", tags=["Iterations"])


def get_service(
    current_user: AzureDevOpsUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> IterationService:
    """Dependency para obter o serviço de iterations."""
    return IterationService(db, token=current_user.token)


@router.get(
    "",
    response_model=IterationsListResponse,
    summary="Listar Iterations (Sprints)",
    description="""
    Lista todas as iterations (sprints) de um projeto/time no Azure DevOps.

    **Retorna:**
    - Lista de iterations com datas de início e fim
    - Campo `timeFrame` indicando se a sprint é `past`, `current` ou `future`
    - ID da iteration atual para pré-seleção no frontend

    **Uso:**
    - Preencher dropdown de seleção de Sprint na Folha de Horas
    - Identificar automaticamente a Sprint atual

    **Permissão necessária:** `vso.work` (leitura de work items)
    """,
)
async def list_iterations(
    organization_name: str = Query(
        ..., description="Nome da organização no Azure DevOps"
    ),
    project_id: str = Query(..., description="ID ou nome do projeto no Azure DevOps"),
    team_id: str | None = Query(
        default=None,
        description="ID ou nome do time (opcional, usa time padrão se omitido)",
    ),
    service: IterationService = Depends(get_service),
) -> IterationsListResponse:
    """Endpoint para listar iterations de um projeto."""
    return await service.list_iterations(
        organization=organization_name,
        project=project_id,
        team=team_id,
    )


@router.get(
    "/{iteration_id}/work-items",
    response_model=IterationWorkItemsResponse,
    summary="Obter Work Items de uma Iteration",
    description="""
    Retorna os IDs dos Work Items associados a uma iteration específica.

    **Retorna:**
    - Lista de IDs de Work Items na iteration
    - Nome da iteration
    - Contagem total

    **Uso:**
    - Filtrar a Folha de Horas por Sprint
    - O frontend pode usar estes IDs para filtrar os work items exibidos

    **Observação:**
    Retorna todos os work items da iteration, incluindo parents (Epic, Feature, Story)
    e tasks/bugs. O relacionamento hierárquico é preservado.
    """,
)
async def get_iteration_work_items(
    iteration_id: str,
    organization_name: str = Query(
        ..., description="Nome da organização no Azure DevOps"
    ),
    project_id: str = Query(..., description="ID ou nome do projeto no Azure DevOps"),
    team_id: str | None = Query(
        default=None,
        description="ID ou nome do time (opcional)",
    ),
    service: IterationService = Depends(get_service),
) -> IterationWorkItemsResponse:
    """Endpoint para obter work items de uma iteration."""
    return await service.get_iteration_work_items(
        organization=organization_name,
        project=project_id,
        iteration_id=iteration_id,
        team=team_id,
    )
