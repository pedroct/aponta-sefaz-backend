import logging
from sqlalchemy.orm import Session
from sqlalchemy import select
from datetime import datetime, timezone
import uuid
import base64
import httpx
from app.models.projeto import Projeto
from app.services.azure import AzureService
from app.auth import AzureDevOpsUser
from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class ProjetoService:
    def __init__(self, db: Session, user: AzureDevOpsUser):
        """
        Inicializa o serviço de projetos.

        Args:
            db: Sessão ativa do banco de dados.
            user: Usuário autenticado com token do Azure DevOps.
        """
        self.db = db
        self.user = user
        # Reutiliza o token do usuário para instanciar o serviço Azure
        self.azure_service = AzureService(token=user.token)

    async def _fetch_projects_from_org(self, org_name: str, pat: str) -> list[dict]:
        """
        Busca projetos de uma organização específica usando PAT.
        
        Args:
            org_name: Nome da organização
            pat: Personal Access Token para a organização
            
        Returns:
            Lista de projetos da organização
        """
        url = f"https://dev.azure.com/{org_name}/_apis/projects?api-version=7.1-preview.1"
        pat_encoded = base64.b64encode(f":{pat}".encode()).decode()
        headers = {"Authorization": f"Basic {pat_encoded}"}
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url, headers=headers)
            
            if response.status_code != 200:
                logger.error(f"Erro ao buscar projetos de {org_name}: {response.status_code} - {response.text}")
                return []
            
            data = response.json()
            projects = data.get("value", [])
            
            # Adiciona o nome da organização em cada projeto
            for project in projects:
                project["_organization"] = org_name
            
            return projects

    async def sync_projects(self) -> dict:
        """
        Busca projetos de TODAS as organizações Azure DevOps configuradas e atualiza o banco local.
        Realiza upsert baseado no external_id.
        """
        logger.info(f"Iniciando sincronização de projetos para usuário: {self.user.display_name}")

        # Obter todas as organizações configuradas
        organizations = settings.get_all_organizations()
        
        if not organizations:
            logger.warning("Nenhuma organização configurada para sincronização")
            return {
                "total_azure": 0,
                "synced": 0,
                "created": 0,
                "updated": 0,
                "organizations": [],
            }
        
        logger.info(f"Sincronizando projetos de {len(organizations)} organização(ões): {[org['name'] for org in organizations]}")

        all_projects = []
        org_results = []
        
        # Buscar projetos de cada organização
        for org in organizations:
            org_name = org["name"]
            pat = org["pat"]
            
            try:
                projects = await self._fetch_projects_from_org(org_name, pat)
                logger.info(f"Recebidos {len(projects)} projetos de {org_name}")
                all_projects.extend(projects)
                org_results.append({"organization": org_name, "count": len(projects), "status": "success"})
            except Exception as e:
                logger.error(f"Erro ao buscar projetos de {org_name}: {e}")
                org_results.append({"organization": org_name, "count": 0, "status": "error", "error": str(e)})

        logger.info(f"Total de {len(all_projects)} projetos recebidos de todas as organizações")

        synced_count = 0
        created_count = 0
        updated_count = 0

        for params in all_projects:
            # Azure ID (UUID)
            ext_id_str = params.get("id")
            if not ext_id_str:
                continue

            try:
                ext_id = uuid.UUID(ext_id_str)
            except ValueError:
                continue  # Pula se ID inválido

            # Verifica se já existe
            stmt = select(Projeto).where(Projeto.external_id == ext_id)
            existing = self.db.execute(stmt).scalar_one_or_none()

            # Mapeamento de campos
            nome = params.get("name")
            descricao = params.get("description")
            url = params.get("url")
            estado = params.get("state")
            organizacao = params.get("_organization")
            now = datetime.now(timezone.utc)

            if existing:
                # Update
                existing.nome = nome
                existing.descricao = descricao
                existing.url = url
                existing.estado = estado
                existing.organizacao = organizacao
                existing.last_sync_at = now
                updated_count += 1
            else:
                # Create
                new_proj = Projeto(
                    external_id=ext_id,
                    nome=nome,
                    descricao=descricao,
                    url=url,
                    estado=estado,
                    organizacao=organizacao,
                    last_sync_at=now,
                )
                self.db.add(new_proj)
                self.db.flush()  # Flush imediatamente após adicionar
                created_count += 1

            synced_count += 1

        try:
            self.db.commit()
            logger.info(f"Sincronização concluída: {created_count} criados, {updated_count} atualizados")
        except Exception as e:
            logger.error(f"Erro ao salvar projetos no banco: {e}")
            self.db.rollback()
            raise

        return {
            "total_azure": len(all_projects),
            "synced": synced_count,
            "created": created_count,
            "updated": updated_count,
            "organizations": org_results,
        }

    def list_local_projects(self) -> list[Projeto]:
        """
        Lista projetos armazenados no cache local (banco de dados).

        Returns:
            Lista de objetos Projeto ordenados por nome.
        """
        return self.db.query(Projeto).order_by(Projeto.nome).all()
