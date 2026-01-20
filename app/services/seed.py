"""
Seed de dados iniciais para desenvolvimento.
"""

import logging
import uuid
from sqlalchemy import inspect
from sqlalchemy.exc import SQLAlchemyError

from app.config import get_settings
from app.database import SessionLocal
from app.models.atividade import Atividade
from app.models.atividade_projeto import AtividadeProjeto
from app.models.projeto import Projeto

logger = logging.getLogger(__name__)


def ensure_seed_data() -> None:
    """Cria dados mínimos para desenvolvimento (projeto e atividades)."""
    settings = get_settings()

    if settings.environment != "development" or not settings.seed_initial_data:
        return

    db = SessionLocal()
    try:
        inspector = inspect(db.get_bind())
        schema = Atividade.__table__.schema
        tables = set(inspector.get_table_names(schema=schema))

        if "atividades" not in tables or "projetos" not in tables:
            logger.info("Seed ignorado: tabelas base ausentes no schema.")
            return

        if "atividade_projeto" not in tables:
            logger.info("Seed ignorado: tabela de relação atividade_projeto ausente.")
            return

        projeto = db.query(Projeto).first()
        if not projeto:
            projeto = Projeto(
                external_id=uuid.uuid4(),
                nome="DEV",
                descricao="Projeto local de desenvolvimento",
                url=None,
                estado="wellFormed",
            )
            db.add(projeto)
            db.flush()

        if db.query(Atividade).count() == 0:
            atividade = Atividade(
                nome="Desenvolvimento",
                descricao="Desenvolvimento de features",
                ativo=True,
                criado_por="seed",
            )
            db.add(atividade)
            db.flush()

            db.add(
                AtividadeProjeto(
                    id_atividade=atividade.id,
                    id_projeto=projeto.id,
                )
            )

        db.commit()
        logger.info("Seed de desenvolvimento aplicado com sucesso.")
    except SQLAlchemyError as exc:
        db.rollback()
        logger.warning(f"Seed falhou: {exc}")
    finally:
        db.close()
