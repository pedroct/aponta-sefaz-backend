"""
Endpoints para busca de Work Items no Azure DevOps.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from app.auth import get_current_user, AzureDevOpsUser
from app.services.azure import AzureService
from app.schemas.work_item import WorkItemSearchResponse

router = APIRouter(prefix="/work-items", tags=["Work Items"])


@router.get(
    "/search",
    response_model=WorkItemSearchResponse,
    summary="Buscar work items",
    description="Busca work items por ID ou título (Azure DevOps).",
)
async def search_work_items(
    query: str = Query(..., min_length=2, description="Texto ou ID para busca"),
    project_id: str | None = Query(
        None, description="ID ou nome do projeto (Azure DevOps)"
    ),
    organization_name: str | None = Query(
        None, description="Nome da organização no Azure DevOps"
    ),
    limit: int = Query(10, ge=1, le=50, description="Limite de resultados"),
    current_user: AzureDevOpsUser = Depends(get_current_user),
) -> WorkItemSearchResponse:
    """Endpoint para busca de work items no Azure DevOps."""
    if not current_user.token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de acesso não disponível para este usuário.",
        )

    service = AzureService(token=current_user.token)
    results = await service.search_work_items(
        query=query,
        project_id=project_id,
        organization_name=organization_name,
        limit=limit,
    )
    return WorkItemSearchResponse(results=results, count=len(results))
