"""
Service para gerenciamento de PATs de organizações Azure DevOps.
"""

import httpx
import logging
from uuid import UUID
from typing import Optional
from sqlalchemy.orm import Session

from app.repositories.organization_pat import OrganizationPatRepository
from app.schemas.organization_pat import (
    OrganizationPatCreate,
    OrganizationPatUpdate,
    OrganizationPatResponse,
    OrganizationPatValidateResponse,
)
from app.config import get_settings

logger = logging.getLogger(__name__)


class OrganizationPatService:
    """Service para operações de PATs de organizações."""

    def __init__(self, db: Session):
        self.db = db
        self.repository = OrganizationPatRepository(db)
        self.settings = get_settings()

    async def validate_pat(
        self, 
        organization_name: str, 
        pat: str
    ) -> OrganizationPatValidateResponse:
        """
        Valida se um PAT é válido para uma organização.
        Tenta listar os projetos da organização usando o PAT.
        """
        url = f"https://dev.azure.com/{organization_name}/_apis/projects?api-version=7.1"
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    url,
                    auth=("", pat),
                )
                
                if response.status_code == 200:
                    data = response.json()
                    projects = [p.get("name", "") for p in data.get("value", [])]
                    return OrganizationPatValidateResponse(
                        valid=True,
                        organization_name=organization_name,
                        message=f"PAT válido. {len(projects)} projeto(s) encontrado(s).",
                        projects_count=len(projects),
                        projects=projects[:10]  # Limita a 10 projetos na resposta
                    )
                elif response.status_code == 401:
                    return OrganizationPatValidateResponse(
                        valid=False,
                        organization_name=organization_name,
                        message="PAT inválido ou expirado (401 Unauthorized).",
                        projects_count=None,
                        projects=None
                    )
                elif response.status_code == 302:
                    return OrganizationPatValidateResponse(
                        valid=False,
                        organization_name=organization_name,
                        message="PAT não tem acesso a esta organização (302 Redirect).",
                        projects_count=None,
                        projects=None
                    )
                else:
                    return OrganizationPatValidateResponse(
                        valid=False,
                        organization_name=organization_name,
                        message=f"Erro inesperado: HTTP {response.status_code}",
                        projects_count=None,
                        projects=None
                    )
        except httpx.TimeoutException:
            return OrganizationPatValidateResponse(
                valid=False,
                organization_name=organization_name,
                message="Timeout ao conectar com Azure DevOps.",
                projects_count=None,
                projects=None
            )
        except Exception as e:
            logger.error(f"Erro ao validar PAT para {organization_name}: {e}")
            return OrganizationPatValidateResponse(
                valid=False,
                organization_name=organization_name,
                message=f"Erro ao validar: {str(e)}",
                projects_count=None,
                projects=None
            )

    def list_all(
        self, 
        skip: int = 0, 
        limit: int = 100,
        only_active: bool = False
    ) -> tuple[list[OrganizationPatResponse], int]:
        """Lista todos os PATs cadastrados."""
        items, total = self.repository.list_all(skip, limit, only_active)
        
        responses = []
        for item in items:
            responses.append(OrganizationPatResponse(
                id=item.id,
                organization_name=item.organization_name,
                organization_url=item.organization_url,
                pat_masked=item.pat_masked,
                descricao=item.descricao,
                expira_em=item.expira_em,
                ativo=item.ativo,
                criado_por=item.criado_por,
                criado_em=item.criado_em,
                atualizado_em=item.atualizado_em,
                status_validacao="não verificado"
            ))
        
        return responses, total

    async def create(
        self, 
        data: OrganizationPatCreate, 
        criado_por: str = None,
        validate_first: bool = True
    ) -> OrganizationPatResponse:
        """
        Cria um novo PAT de organização.
        Opcionalmente valida o PAT antes de salvar.
        """
        # Valida o PAT antes de salvar (opcional)
        validation_status = "não verificado"
        if validate_first:
            validation = await self.validate_pat(data.organization_name, data.pat)
            if not validation.valid:
                raise ValueError(f"PAT inválido: {validation.message}")
            validation_status = "válido"
        
        # Cria no banco
        org_pat = self.repository.create(data, criado_por)
        
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
            status_validacao=validation_status
        )

    def update(
        self, 
        pat_id: UUID, 
        data: OrganizationPatUpdate
    ) -> Optional[OrganizationPatResponse]:
        """Atualiza um PAT existente."""
        org_pat = self.repository.update(pat_id, data)
        
        if not org_pat:
            return None
        
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

    def delete(self, pat_id: UUID) -> bool:
        """Remove um PAT."""
        return self.repository.delete(pat_id)

    def get_by_id(self, pat_id: UUID) -> Optional[OrganizationPatResponse]:
        """Busca um PAT pelo ID."""
        org_pat = self.repository.get_by_id(pat_id)
        
        if not org_pat:
            return None
        
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

    def get_pat_for_organization(self, organization_name: str) -> Optional[str]:
        """
        Retorna o PAT para uma organização.
        Primeiro busca no banco de dados, depois nas variáveis de ambiente.
        """
        # 1. Busca no banco de dados
        pat = self.repository.get_pat_for_organization(organization_name)
        if pat:
            logger.debug(f"PAT encontrado no banco para {organization_name}")
            return pat
        
        # 2. Fallback: busca nas variáveis de ambiente
        pat = self.settings.get_pat_for_org(organization_name)
        if pat:
            logger.debug(f"PAT encontrado nas variáveis de ambiente para {organization_name}")
            return pat
        
        logger.warning(f"Nenhum PAT encontrado para {organization_name}")
        return None

    async def validate_stored_pat(self, pat_id: UUID) -> OrganizationPatValidateResponse:
        """Valida um PAT já armazenado no banco."""
        org_pat = self.repository.get_by_id(pat_id)
        
        if not org_pat:
            return OrganizationPatValidateResponse(
                valid=False,
                organization_name="",
                message="PAT não encontrado.",
                projects_count=None,
                projects=None
            )
        
        pat = org_pat.get_pat()
        return await self.validate_pat(org_pat.organization_name, pat)
