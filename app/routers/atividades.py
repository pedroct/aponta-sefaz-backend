"""
Endpoints REST para CRUD de Atividades.
Todos os endpoints são protegidos por autenticação Azure DevOps.

A relação entre Atividades e Projetos é N:N (muitos para muitos),
permitindo que uma atividade seja associada a múltiplos projetos.
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
    AtividadeCatalogResponse,
    AtividadeCatalogItem,
)

router = APIRouter(prefix="/atividades", tags=["Atividades"])


@router.post(
    "",
    response_model=AtividadeResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Criar atividade",
    description="""
    Cria uma nova atividade no sistema associada a um ou mais projetos.

    **Novo formato (N:N):**
    - `ids_projetos`: Lista de UUIDs dos projetos (obrigatório, mínimo 1)

    **Retrocompatibilidade:**
    - `id_projeto`: UUID do projeto (aceito, convertido para ids_projetos)
    """,
)
def criar_atividade(
    atividade: AtividadeCreate,
    current_user: AzureDevOpsUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> AtividadeResponse:
    """Endpoint para criar uma nova atividade."""
    repository = AtividadeRepository(db)
    # Usar email do usuário autenticado, ou display_name como fallback
    criado_por = current_user.email or current_user.display_name

    try:
        return repository.create(atividade, criado_por=criado_por)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get(
    "",
    response_model=AtividadeCatalogResponse,
    summary="Listar atividades",
    description="""
    Lista todas as atividades com paginação e filtros opcionais.

    O filtro `id_projeto` retorna atividades que **contêm** o projeto especificado
    (uma atividade pode estar em múltiplos projetos).
    """,
)
def listar_atividades(
    skip: int = Query(0, ge=0, description="Registros a pular"),
    limit: int = Query(100, ge=1, le=1000, description="Máximo de registros"),
    ativo: bool | None = Query(None, description="Filtrar por status ativo"),
    id_projeto: UUID | None = Query(
        None, description="Filtrar por projeto (retorna atividades que contêm este projeto)"
    ),
    current_user: AzureDevOpsUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> AtividadeCatalogResponse:
    """Endpoint para listar atividades no formato esperado pelo frontend."""
    repository = AtividadeRepository(db)
    atividades, _ = repository.get_all(
        skip=skip, limit=limit, ativo=ativo, id_projeto=id_projeto
    )

    atividades_ordenadas = sorted(atividades, key=lambda item: (item.nome or ""))
    items = [
        AtividadeCatalogItem(
            id=str(atividade.id),
            nome=atividade.nome,
            descricao=atividade.descricao,
            ativo=atividade.ativo,
            order=index + 1,
        )
        for index, atividade in enumerate(atividades_ordenadas)
    ]

    return AtividadeCatalogResponse(items=items)


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
    description="""
    Atualiza uma atividade existente.

    **Atualizando projetos:**
    - `ids_projetos`: Lista de UUIDs substitui **todos** os projetos associados
    - `id_projeto`: UUID único (retrocompatibilidade, convertido para ids_projetos)
    """,
)
def atualizar_atividade(
    atividade_id: UUID,
    atividade: AtividadeUpdate,
    current_user: AzureDevOpsUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> AtividadeResponse:
    """Endpoint para atualizar uma atividade."""
    repository = AtividadeRepository(db)

    try:
        atividade_atualizada = repository.update(atividade_id, atividade)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

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
