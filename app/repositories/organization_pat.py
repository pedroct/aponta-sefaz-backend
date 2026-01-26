"""
Repository para operações de banco de dados de PATs de organizações.
"""

from uuid import UUID
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.models.organization_pat import OrganizationPat
from app.schemas.organization_pat import OrganizationPatCreate, OrganizationPatUpdate


class OrganizationPatRepository:
    """Repository para operações CRUD de OrganizationPat."""

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, pat_id: UUID) -> Optional[OrganizationPat]:
        """Busca um PAT pelo ID."""
        return self.db.query(OrganizationPat).filter(
            OrganizationPat.id == pat_id
        ).first()

    def get_by_organization(self, organization_name: str) -> Optional[OrganizationPat]:
        """Busca um PAT pelo nome da organização."""
        return self.db.query(OrganizationPat).filter(
            OrganizationPat.organization_name == organization_name.lower().strip()
        ).first()

    def get_active_by_organization(self, organization_name: str) -> Optional[OrganizationPat]:
        """Busca um PAT ativo pelo nome da organização."""
        return self.db.query(OrganizationPat).filter(
            OrganizationPat.organization_name == organization_name.lower().strip(),
            OrganizationPat.ativo == True
        ).first()

    def list_all(
        self, 
        skip: int = 0, 
        limit: int = 100,
        only_active: bool = False
    ) -> tuple[list[OrganizationPat], int]:
        """Lista todos os PATs com paginação."""
        query = self.db.query(OrganizationPat)
        
        if only_active:
            query = query.filter(OrganizationPat.ativo == True)
        
        total = query.count()
        items = query.order_by(OrganizationPat.organization_name).offset(skip).limit(limit).all()
        
        return items, total

    def create(self, data: OrganizationPatCreate, criado_por: str = None) -> OrganizationPat:
        """Cria um novo registro de PAT."""
        # Verifica se já existe
        existing = self.get_by_organization(data.organization_name)
        if existing:
            raise ValueError(f"Já existe um PAT cadastrado para a organização '{data.organization_name}'")
        
        # Cria o objeto
        org_pat = OrganizationPat(
            organization_name=data.organization_name.lower().strip(),
            organization_url=data.organization_url or f"https://dev.azure.com/{data.organization_name}",
            descricao=data.descricao,
            expira_em=data.expira_em,
            ativo=data.ativo,
            criado_por=criado_por,
        )
        
        # Criptografa e armazena o PAT
        org_pat.set_pat(data.pat)
        
        self.db.add(org_pat)
        self.db.commit()
        self.db.refresh(org_pat)
        
        return org_pat

    def update(
        self, 
        pat_id: UUID, 
        data: OrganizationPatUpdate
    ) -> Optional[OrganizationPat]:
        """Atualiza um registro de PAT existente."""
        org_pat = self.get_by_id(pat_id)
        if not org_pat:
            return None
        
        # Atualiza os campos fornecidos
        if data.organization_url is not None:
            org_pat.organization_url = data.organization_url
        if data.descricao is not None:
            org_pat.descricao = data.descricao
        if data.expira_em is not None:
            org_pat.expira_em = data.expira_em
        if data.ativo is not None:
            org_pat.ativo = data.ativo
        if data.pat is not None:
            org_pat.set_pat(data.pat)
        
        self.db.commit()
        self.db.refresh(org_pat)
        
        return org_pat

    def delete(self, pat_id: UUID) -> bool:
        """Remove um registro de PAT."""
        org_pat = self.get_by_id(pat_id)
        if not org_pat:
            return False
        
        self.db.delete(org_pat)
        self.db.commit()
        
        return True

    def toggle_active(self, pat_id: UUID) -> Optional[OrganizationPat]:
        """Alterna o status ativo/inativo de um PAT."""
        org_pat = self.get_by_id(pat_id)
        if not org_pat:
            return None
        
        org_pat.ativo = not org_pat.ativo
        self.db.commit()
        self.db.refresh(org_pat)
        
        return org_pat

    def get_pat_for_organization(self, organization_name: str) -> Optional[str]:
        """
        Retorna o PAT descriptografado para uma organização.
        Usado internamente pelo serviço de timesheet.
        """
        org_pat = self.get_active_by_organization(organization_name)
        if org_pat:
            return org_pat.get_pat()
        return None

    def search(self, query: str) -> list[OrganizationPat]:
        """Busca PATs por nome de organização ou descrição."""
        search_term = f"%{query.lower()}%"
        return self.db.query(OrganizationPat).filter(
            or_(
                OrganizationPat.organization_name.ilike(search_term),
                OrganizationPat.descricao.ilike(search_term)
            )
        ).all()
