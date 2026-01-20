"""
Endpoints REST para CRUD de Apontamentos (Registro de Horas).
Todos os endpoints sao protegidos por autenticacao Azure DevOps.
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
    """Dependency para obter o servico de apontamentos."""
    return ApontamentoService(db, token=current_user.token)


@router.post(
    "",
    response_model=ApontamentoResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Criar apontamento",
    description="""
    Cria um novo registro de horas trabalhadas.

    **Dados obrigatorios do Azure DevOps:**
    - `work_item_id`: ID do Work Item (Task ou Bug)
    - `project_id`: ID do projeto (IProjectInfo.id)
    - `organization_name`: Nome da organizacao (IHostContext.name)
    - `usuario_id`: ID do usuario (IUserContext.id)
    - `usuario_nome`: Nome do usuario (IUserContext.displayName)

    **Dados do formulario:**
    - `data_apontamento`: Data do trabalho (YYYY-MM-DD)
    - `duracao`: Duracao no formato HH:mm (ex: 01:00, 02:30, 08:00)
    - `id_atividade`: ID da atividade/tipo de atividade selecionada
    - `comentario`: Comentario opcional (max 500 caracteres)

    Apos criar o apontamento, os campos CompletedWork e RemainingWork do work item
    no Azure DevOps sao automaticamente atualizados.
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
    Lista todos os apontamentos de um work item especifico com paginacao.

    Retorna tambem o total de horas apontadas em formato decimal e formatado (HH:mm).
    """,
)
def listar_apontamentos_work_item(
    work_item_id: int,
    organization_name: str = Query(..., description="Nome da organizacao no Azure DevOps"),
    project_id: str = Query(..., description="ID do projeto no Azure DevOps"),
    skip: int = Query(0, ge=0, description="Registros a pular"),
    limit: int = Query(100, ge=1, le=1000, description="Maximo de registros"),
    service: ApontamentoService = Depends(get_service),
) -> ApontamentoListResponse:
    """Endpoint para listar apontamentos de um work item."""
    apontamentos, total, total_horas, total_formatado = service.listar_por_work_item(
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
        total_formatado=total_formatado,
    )


@router.get(
    "/work-item/{work_item_id}/resumo",
    response_model=ApontamentoResumo,
    summary="Resumo de apontamentos de um work item",
    description="""
    Retorna um resumo dos apontamentos de um work item especifico.

    Inclui total de apontamentos e tempo total apontado.
    """,
)
def resumo_apontamentos_work_item(
    work_item_id: int,
    organization_name: str = Query(..., description="Nome da organizacao no Azure DevOps"),
    project_id: str = Query(..., description="ID do projeto no Azure DevOps"),
    service: ApontamentoService = Depends(get_service),
) -> ApontamentoResumo:
    """Endpoint para obter resumo de apontamentos de um work item."""
    resumo = service.resumo_por_work_item(
        work_item_id=work_item_id,
        organization_name=organization_name,
        project_id=project_id,
    )

    return ApontamentoResumo(**resumo)


@router.get(
    "/work-item/{work_item_id}/azure-info",
    summary="Informacoes do work item no Azure DevOps",
    description="""
    Obtem as informacoes de tempo do work item diretamente do Azure DevOps.

    Retorna:
    - `originalEstimate`: Estimativa original (horas)
    - `remainingWork`: Trabalho restante (horas)
    - `completedWork`: Trabalho completado (horas)
    """,
)
async def info_work_item_azure(
    work_item_id: int,
    organization_name: str = Query(..., description="Nome da organizacao no Azure DevOps"),
    project_id: str = Query(..., description="ID do projeto no Azure DevOps"),
    service: ApontamentoService = Depends(get_service),
) -> dict:
    """Endpoint para obter informacoes do work item do Azure DevOps."""
    return await service.get_work_item_info(
        organization=organization_name,
        project=project_id,
        work_item_id=work_item_id,
    )


@router.get(
    "/{apontamento_id}",
    response_model=ApontamentoResponse,
    summary="Obter apontamento",
    description="Obtem um apontamento especifico por ID.",
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
            detail=f"Apontamento com ID {apontamento_id} nao encontrado",
        )

    return apontamento


@router.put(
    "/{apontamento_id}",
    response_model=ApontamentoResponse,
    summary="Atualizar apontamento",
    description="""
    Atualiza um apontamento existente.

    Apos atualizar, os campos CompletedWork e RemainingWork do work item no Azure DevOps
    sao automaticamente recalculados.
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

    Apos excluir, os campos CompletedWork e RemainingWork do work item no Azure DevOps
    sao automaticamente recalculados.
    """,
)
async def excluir_apontamento(
    apontamento_id: UUID,
    service: ApontamentoService = Depends(get_service),
) -> None:
    """Endpoint para excluir um apontamento."""
    await service.excluir_apontamento(apontamento_id)
