"""
Endpoints REST para Timesheet (Folha de Horas).
Fornece a grade semanal com hierarquia de Work Items e apontamentos.
"""

from datetime import date
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.auth import AzureDevOpsUser, get_current_user
from app.database import get_db
from app.schemas.timesheet import (
    StateCategoryResponse,
    TimesheetResponse,
)
from app.services.timesheet_service import TimesheetService

router = APIRouter(prefix="/timesheet", tags=["Timesheet"])


def get_service(
    current_user: AzureDevOpsUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> TimesheetService:
    """Dependency para obter o serviço de timesheet."""
    return TimesheetService(db, token=current_user.token)


@router.get(
    "",
    response_model=TimesheetResponse,
    summary="Obter timesheet semanal",
    description="""
    Retorna a grade semanal (Folha de Horas) com a hierarquia de Work Items
    e apontamentos agregados por dia.

    **Hierarquia:**
    - Epic (nível 0)
    - Feature (nível 1)
    - User Story / PBI (nível 2)
    - Task / Bug (nível 3)

    **Colunas:**
    - **E (Esforço)**: OriginalEstimate do Azure DevOps
    - **H (Histórico)**: Total de horas apontadas na semana
    - **Dias da semana**: Apontamentos por dia (segunda a domingo)
    - **SEMANAL Σ**: Soma total da semana por Work Item

    **Filtros:**
    - `current_project_only`: Filtra apenas do projeto informado (implícito)
    - Apenas itens atribuídos ao usuário logado são exibidos

    **Permissões de edição:**
    - Work Items em estados **Proposed**, **InProgress** ou **Resolved**: permitem edição/exclusão
    - Work Items em estados **Completed** ou **Removed**: bloqueiam edição/exclusão
    """,
)
async def get_timesheet(
    organization_name: str = Query(
        ..., description="Nome da organização no Azure DevOps"
    ),
    project_id: str = Query(..., description="ID do projeto no Azure DevOps"),
    week_start: date | None = Query(
        default=None,
        description="Data de início da semana (segunda-feira). Se não informado, usa a semana atual.",
    ),
    current_user: AzureDevOpsUser = Depends(get_current_user),
    service: TimesheetService = Depends(get_service),
) -> TimesheetResponse:
    """Endpoint para obter o timesheet semanal."""
    return await service.get_timesheet(
        organization=organization_name,
        project=project_id,
        week_start=week_start,
        user_email=current_user.email,
        user_id=current_user.id,
    )


@router.get(
    "/work-item/{work_item_id}/state-category",
    response_model=StateCategoryResponse,
    summary="Verificar categoria de estado do Work Item",
    description="""
    Retorna a categoria de estado de um Work Item específico e as permissões
    de edição/exclusão de apontamentos.

    **Categorias de estado (Agile Process):**
    - **Proposed**: New → permite edição
    - **InProgress**: Active, Committed, Open → permite edição
    - **Resolved**: Resolved → permite edição
    - **Completed**: Closed, Done → **bloqueia** edição
    - **Removed**: Removed → **bloqueia** edição

    Use este endpoint antes de permitir edição/exclusão de um apontamento
    para validar se a operação é permitida.
    """,
)
async def get_work_item_state_category(
    work_item_id: int,
    organization_name: str = Query(
        ..., description="Nome da organização no Azure DevOps"
    ),
    project_id: str = Query(..., description="ID do projeto no Azure DevOps"),
    service: TimesheetService = Depends(get_service),
) -> StateCategoryResponse:
    """Endpoint para verificar a categoria de estado de um Work Item."""
    return await service.get_state_category(
        organization=organization_name,
        project=project_id,
        work_item_id=work_item_id,
    )
