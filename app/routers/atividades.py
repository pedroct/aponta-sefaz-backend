"""
Endpoints REST para CRUD de Atividades.
Todos os endpoints são protegidos por autenticação Azure DevOps.
"""

from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.auth import get_current_user, AzureDevOpsUser
from app.repositories.atividade import AtividadeRepository
from app.schemas.atividade import (
    AtividadeCreate,
    AtividadeUpdate,
    AtividadeResponse,
    AtividadeListResponse,
)

router = APIRouter(prefix="/atividades", tags=["Atividades"])


@router.post(
    "",
    response_model=AtividadeResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Criar atividade",
    description="Cria uma nova atividade no sistema.",
)
def criar_atividade(
    atividade: AtividadeCreate,
    current_user: AzureDevOpsUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> AtividadeResponse:
    """Endpoint para criar uma nova atividade."""
    repository = AtividadeRepository(db)
    return repository.create(atividade)


@router.get(
    "",
    response_model=AtividadeListResponse,
    summary="Listar atividades",
    description="Lista todas as atividades com paginação e filtros opcionais.",
)
def listar_atividades(
    skip: int = Query(0, ge=0, description="Registros a pular"),
    limit: int = Query(100, ge=1, le=1000, description="Máximo de registros"),
    ativo: bool | None = Query(None, description="Filtrar por status ativo"),
    id_projeto: UUID | None = Query(None, description="Filtrar por projeto"),
    current_user: AzureDevOpsUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> AtividadeListResponse:
    """Endpoint para listar atividades com paginação."""
    repository = AtividadeRepository(db)
    atividades, total = repository.get_all(
        skip=skip, limit=limit, ativo=ativo, id_projeto=id_projeto
    )
    return AtividadeListResponse(items=atividades, total=total)


@router.get(
    "/{atividade_id}",
    response_model=AtividadeResponse,
    summary="Obter atividade",
    description="Obtém uma atividade específica por ID.",
)
def obter_atividade(
    atividade_id: UUID,
    current_user: AzureDevOpsUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> AtividadeResponse:
    """Endpoint para obter uma atividade por ID."""
    repository = AtividadeRepository(db)
    atividade = repository.get_by_id(atividade_id)

    if not atividade:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Atividade com ID {atividade_id} não encontrada",
        )

    return atividade


@router.put(
    "/{atividade_id}",
    response_model=AtividadeResponse,
    summary="Atualizar atividade",
    description="Atualiza uma atividade existente.",
)
def atualizar_atividade(
    atividade_id: UUID,
    atividade: AtividadeUpdate,
    current_user: AzureDevOpsUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> AtividadeResponse:
    """Endpoint para atualizar uma atividade."""
    repository = AtividadeRepository(db)
    atividade_atualizada = repository.update(atividade_id, atividade)

    if not atividade_atualizada:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Atividade com ID {atividade_id} não encontrada",
        )

    return atividade_atualizada


@router.delete(
    "/{atividade_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Excluir atividade",
    description="Remove uma atividade do sistema.",
)
def excluir_atividade(
    atividade_id: UUID,
    current_user: AzureDevOpsUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    """Endpoint para excluir uma atividade."""
    repository = AtividadeRepository(db)
    deleted = repository.delete(atividade_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Atividade com ID {atividade_id} não encontrada",
        )
