"""
Endpoints REST para gerenciamento de PATs de organizações Azure DevOps.
Todos os endpoints são protegidos por autenticação.
"""

from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.auth import get_current_user, AzureDevOpsUser
from app.services.organization_pat_service import OrganizationPatService
from app.schemas.organization_pat import (
    OrganizationPatCreate,
    OrganizationPatUpdate,
    OrganizationPatResponse,
    OrganizationPatList,
    OrganizationPatValidateRequest,
    OrganizationPatValidateResponse,
)

router = APIRouter(prefix="/organization-pats", tags=["Organization PATs"])


@router.get(
    "",
    response_model=OrganizationPatList,
    summary="Listar PATs",
    description="Lista todos os PATs de organizações cadastrados.",
)
async def listar_pats(
    skip: int = Query(0, ge=0, description="Registros a pular"),
    limit: int = Query(100, ge=1, le=500, description="Limite de registros"),
    only_active: bool = Query(False, description="Apenas PATs ativos"),
    current_user: AzureDevOpsUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> OrganizationPatList:
    """Lista todos os PATs cadastrados."""
    service = OrganizationPatService(db)
    items, total = service.list_all(skip, limit, only_active)
    
    return OrganizationPatList(items=items, total=total)


@router.get(
    "/{pat_id}",
    response_model=OrganizationPatResponse,
    summary="Buscar PAT por ID",
    description="Retorna os detalhes de um PAT específico.",
)
async def buscar_pat(
    pat_id: UUID,
    current_user: AzureDevOpsUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> OrganizationPatResponse:
    """Busca um PAT pelo ID."""
    service = OrganizationPatService(db)
    pat = service.get_by_id(pat_id)
    
    if not pat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="PAT não encontrado",
        )
    
    return pat


@router.post(
    "",
    response_model=OrganizationPatResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Criar PAT",
    description="""
    Cadastra um novo PAT para uma organização Azure DevOps.
    O PAT será criptografado antes de ser armazenado.
    Por padrão, o PAT é validado antes de ser salvo.
    """,
)
async def criar_pat(
    data: OrganizationPatCreate,
    validate_first: bool = Query(True, description="Validar PAT antes de salvar"),
    current_user: AzureDevOpsUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> OrganizationPatResponse:
    """Cria um novo PAT de organização."""
    service = OrganizationPatService(db)
    criado_por = current_user.email or current_user.display_name
    
    try:
        return await service.create(data, criado_por, validate_first)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.put(
    "/{pat_id}",
    response_model=OrganizationPatResponse,
    summary="Atualizar PAT",
    description="Atualiza os dados de um PAT existente.",
)
async def atualizar_pat(
    pat_id: UUID,
    data: OrganizationPatUpdate,
    current_user: AzureDevOpsUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> OrganizationPatResponse:
    """Atualiza um PAT existente."""
    service = OrganizationPatService(db)
    pat = service.update(pat_id, data)
    
    if not pat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="PAT não encontrado",
        )
    
    return pat


@router.delete(
    "/{pat_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remover PAT",
    description="Remove um PAT do sistema.",
)
async def remover_pat(
    pat_id: UUID,
    current_user: AzureDevOpsUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Remove um PAT."""
    service = OrganizationPatService(db)
    deleted = service.delete(pat_id)
    
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="PAT não encontrado",
        )


@router.post(
    "/validate",
    response_model=OrganizationPatValidateResponse,
    summary="Validar PAT",
    description="Valida se um PAT é válido para uma organização (sem salvar).",
)
async def validar_pat(
    data: OrganizationPatValidateRequest,
    current_user: AzureDevOpsUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> OrganizationPatValidateResponse:
    """Valida um PAT sem salvar."""
    service = OrganizationPatService(db)
    return await service.validate_pat(data.organization_name, data.pat)


@router.post(
    "/{pat_id}/validate",
    response_model=OrganizationPatValidateResponse,
    summary="Validar PAT armazenado",
    description="Valida se um PAT já cadastrado ainda é válido.",
)
async def validar_pat_armazenado(
    pat_id: UUID,
    current_user: AzureDevOpsUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> OrganizationPatValidateResponse:
    """Valida um PAT já armazenado."""
    service = OrganizationPatService(db)
    return await service.validate_stored_pat(pat_id)


@router.post(
    "/{pat_id}/toggle-active",
    response_model=OrganizationPatResponse,
    summary="Alternar status ativo",
    description="Alterna o status ativo/inativo de um PAT.",
)
async def alternar_status(
    pat_id: UUID,
    current_user: AzureDevOpsUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> OrganizationPatResponse:
    """Alterna o status ativo/inativo de um PAT."""
    service = OrganizationPatService(db)
    from app.repositories.organization_pat import OrganizationPatRepository
    
    repository = OrganizationPatRepository(db)
    org_pat = repository.toggle_active(pat_id)
    
    if not org_pat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="PAT não encontrado",
        )
    
    return OrganizationPatResponse(
        id=org_pat.id,
        organization_name=org_pat.organization_name,
        organization_url=org_pat.organization_url,
        pat_masked=org_pat.pat_masked,
        descricao=org_pat.descricao,
        expira_em=org_pat.expira_em,
        ativo=org_pat.ativo,
        criado_por=org_pat.criado_por,
        criado_em=org_pat.criado_em,
        atualizado_em=org_pat.atualizado_em,
        status_validacao="não verificado"
    )
