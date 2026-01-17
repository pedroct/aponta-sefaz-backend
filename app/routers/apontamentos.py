"""
Endpoints REST para CRUD de Apontamentos (Registro de Horas).
Todos os endpoints são protegidos por autenticação Azure DevOps.
"""

from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.auth import get_current_user, AzureDevOpsUser
from app.services.apontamento_service import ApontamentoService
from app.repositories.apontamento import ApontamentoRepository
from app.schemas.apontamento import (
    ApontamentoCreate,
    ApontamentoUpdate,
    ApontamentoResponse,
    ApontamentoListResponse,
    ApontamentoResumo,
)

router = APIRouter(prefix="/apontamentos", tags=["Apontamentos"])


def get_service(
    current_user: AzureDevOpsUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ApontamentoService:
    """Dependency para obter o serviço de apontamentos."""
    return ApontamentoService(db, token=current_user.token)


@router.post(
    "",
    response_model=ApontamentoResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Criar apontamento",
    description="""
    Cria um novo registro de horas trabalhadas.

    **Dados obrigatórios do Azure DevOps:**
    - `work_item_id`: ID do Work Item
    - `project_id`: ID do projeto (IProjectInfo.id)
    - `organization_name`: Nome da organização (IHostContext.name)
    - `usuario_id`: ID do usuário (IUserContext.id)
    - `usuario_nome`: Nome do usuário (IUserContext.displayName)

    **Dados do formulário:**
    - `data_apontamento`: Data do trabalho (YYYY-MM-DD)
    - `horas`: Horas trabalhadas (0-8)
    - `minutos`: Minutos trabalhados (0, 15, 30, 45)
    - `id_atividade`: ID da atividade selecionada
    - `comentario`: Comentário opcional (máx 100 caracteres)

    Após criar o apontamento, o campo CompletedWork do work item
    no Azure DevOps é automaticamente atualizado.
    """,
)
async def criar_apontamento(
    apontamento: ApontamentoCreate,
    service: ApontamentoService = Depends(get_service),
) -> ApontamentoResponse:
    """Endpoint para criar um novo apontamento."""
    return await service.criar_apontamento(apontamento)


@router.get(
    "/work-item/{work_item_id}",
    response_model=ApontamentoListResponse,
    summary="Listar apontamentos de um work item",
    description="""
    Lista todos os apontamentos de um work item específico com paginação.

    Retorna também os totais de horas e minutos apontados.
    """,
)
def listar_apontamentos_work_item(
    work_item_id: int,
    organization_name: str = Query(..., description="Nome da organização no Azure DevOps"),
    project_id: str = Query(..., description="ID do projeto no Azure DevOps"),
    skip: int = Query(0, ge=0, description="Registros a pular"),
    limit: int = Query(100, ge=1, le=1000, description="Máximo de registros"),
    service: ApontamentoService = Depends(get_service),
) -> ApontamentoListResponse:
    """Endpoint para listar apontamentos de um work item."""
    apontamentos, total, total_horas, total_minutos = service.listar_por_work_item(
        work_item_id=work_item_id,
        organization_name=organization_name,
        project_id=project_id,
        skip=skip,
        limit=limit,
    )
    return ApontamentoListResponse(
        items=apontamentos,
        total=total,
        total_horas=total_horas,
        total_minutos=total_minutos,
    )


@router.get(
    "/work-item/{work_item_id}/resumo",
    response_model=ApontamentoResumo,
    summary="Resumo de apontamentos de um work item",
    description="""
    Retorna um resumo dos apontamentos de um work item específico.

    Inclui total de apontamentos e tempo total apontado.
    """,
)
def resumo_apontamentos_work_item(
    work_item_id: int,
    organization_name: str = Query(..., description="Nome da organização no Azure DevOps"),
    project_id: str = Query(..., description="ID do projeto no Azure DevOps"),
    service: ApontamentoService = Depends(get_service),
) -> ApontamentoResumo:
    """Endpoint para obter resumo de apontamentos de um work item."""
    _, total, total_horas, total_minutos = service.listar_por_work_item(
        work_item_id=work_item_id,
        organization_name=organization_name,
        project_id=project_id,
        skip=0,
        limit=1,
    )

    # Converter minutos extras em horas para formatação
    horas_extras = total_minutos // 60
    minutos_restantes = total_minutos % 60
    total_horas_final = total_horas + horas_extras

    return ApontamentoResumo(
        work_item_id=work_item_id,
        total_apontamentos=total,
        total_horas=total_horas_final,
        total_minutos=minutos_restantes,
        tempo_total_formatado=f"{total_horas_final:02d}:{minutos_restantes:02d}",
    )


@router.get(
    "/work-item/{work_item_id}/azure-info",
    summary="Informações do work item no Azure DevOps",
    description="""
    Obtém as informações de tempo do work item diretamente do Azure DevOps.

    Retorna:
    - `originalEstimate`: Estimativa original (horas)
    - `remainingWork`: Trabalho restante (horas)
    - `completedWork`: Trabalho completado (horas)
    """,
)
async def info_work_item_azure(
    work_item_id: int,
    organization_name: str = Query(..., description="Nome da organização no Azure DevOps"),
    project_id: str = Query(..., description="ID do projeto no Azure DevOps"),
    service: ApontamentoService = Depends(get_service),
) -> dict:
    """Endpoint para obter informações do work item do Azure DevOps."""
    return await service.get_work_item_info(
        organization=organization_name,
        project=project_id,
        work_item_id=work_item_id,
    )


@router.get(
    "/{apontamento_id}",
    response_model=ApontamentoResponse,
    summary="Obter apontamento",
    description="Obtém um apontamento específico por ID.",
)
def obter_apontamento(
    apontamento_id: UUID,
    current_user: AzureDevOpsUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ApontamentoResponse:
    """Endpoint para obter um apontamento por ID."""
    repository = ApontamentoRepository(db)
    apontamento = repository.get_by_id(apontamento_id)

    if not apontamento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Apontamento com ID {apontamento_id} não encontrado",
        )

    return apontamento


@router.put(
    "/{apontamento_id}",
    response_model=ApontamentoResponse,
    summary="Atualizar apontamento",
    description="""
    Atualiza um apontamento existente.

    Após atualizar, o campo CompletedWork do work item no Azure DevOps
    é automaticamente recalculado.
    """,
)
async def atualizar_apontamento(
    apontamento_id: UUID,
    apontamento: ApontamentoUpdate,
    service: ApontamentoService = Depends(get_service),
) -> ApontamentoResponse:
    """Endpoint para atualizar um apontamento."""
    return await service.atualizar_apontamento(apontamento_id, apontamento)


@router.delete(
    "/{apontamento_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Excluir apontamento",
    description="""
    Remove um apontamento do sistema.

    Após excluir, o campo CompletedWork do work item no Azure DevOps
    é automaticamente recalculado.
    """,
)
async def excluir_apontamento(
    apontamento_id: UUID,
    service: ApontamentoService = Depends(get_service),
) -> None:
    """Endpoint para excluir um apontamento."""
    await service.excluir_apontamento(apontamento_id)
