"""
Alembic Environment Configuration.
Configura migrações com SQLAlchemy.
"""
from logging.config import fileConfig
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context
import os
import sys
import sqlalchemy as sa

# Adicionar o diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.config import get_settings
from app.database import Base
from app.models.atividade import (
    Atividade,
)  # noqa: F401 - Import para registro do modelo

# Configuração do Alembic
config = context.config

# Configurar logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Metadata dos modelos
target_metadata = Base.metadata

# Obter URL do banco
settings = get_settings()
config.set_main_option("sqlalchemy.url", settings.database_url)

# Função helper para migrações acessarem o schema
def get_migration_schema():
    """Retorna o schema que deve ser usado nas migrações."""
    return settings.database_schema


def run_migrations_offline() -> None:
    """Executa migrações em modo 'offline'."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Executa migrações em modo 'online'."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        # Garantir que o schema existe
        if settings.database_schema and settings.database_schema != "public":
            connection.execute(sa.schema.CreateSchema(settings.database_schema, if_not_exists=True))
            connection.commit()

        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            version_table_schema=settings.database_schema,
            include_schemas=True
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
