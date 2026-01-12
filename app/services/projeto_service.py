import logging
from sqlalchemy.orm import Session
from sqlalchemy import select
from datetime import datetime, timezone
import uuid
from app.models.projeto import Projeto
from app.services.azure import AzureService
from app.auth import AzureDevOpsUser

logger = logging.getLogger(__name__)


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

    async def sync_projects(self) -> dict:
        """
        Busca projetos do Azure DevOps e atualiza o banco local.
        Realiza upsert baseado no external_id.
        """
        logger.info(f"Iniciando sincronização de projetos para usuário: {self.user.display_name}")

        # 1. Buscar do Azure
        try:
            azure_projects = await self.azure_service.list_projects()
            logger.info(f"Recebidos {len(azure_projects)} projetos do Azure DevOps")
        except Exception as e:
            logger.error(f"Erro ao buscar projetos do Azure: {e}")
            raise

        synced_count = 0
        created_count = 0
        updated_count = 0

        for params in azure_projects:
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
            now = datetime.now(timezone.utc)

            if existing:
                # Update
                existing.nome = nome
                existing.descricao = descricao
                existing.url = url
                existing.estado = estado
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
            "total_azure": len(azure_projects),
            "synced": synced_count,
            "created": created_count,
            "updated": updated_count,
        }

    def list_local_projects(self) -> list[Projeto]:
        """
        Lista projetos armazenados no cache local (banco de dados).

        Returns:
            Lista de objetos Projeto ordenados por nome.
        """
        return self.db.query(Projeto).order_by(Projeto.nome).all()
