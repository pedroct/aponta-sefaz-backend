from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.auth import get_current_user, AzureDevOpsUser
from app.services.projeto_service import ProjetoService

router = APIRouter(prefix="/api/v1", tags=["Projetos"])


@router.post("/integracao/sincronizar")
async def sync_projects(
    db: Session = Depends(get_db), user: AzureDevOpsUser = Depends(get_current_user)
):
    """
    Sincroniza projetos do Azure DevOps com o banco local.
    """
    service = ProjetoService(db, user)
    result = await service.sync_projects()
    return result


@router.get("/projetos")
def list_projects(
    db: Session = Depends(get_db), user: AzureDevOpsUser = Depends(get_current_user)
):
    """
    Lista projetos do cache local.
    """
    service = ProjetoService(db, user)
    return service.list_local_projects()
