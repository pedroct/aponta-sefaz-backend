"""
Configuração do banco de dados PostgreSQL com SQLAlchemy.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config import get_settings

settings = get_settings()

# Engine de conexão
# Adicionamos search_path para garantir que o schema correto seja o padrão da conexão
engine = create_engine(
    settings.database_url_resolved,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
    connect_args={"options": f"-c search_path=\"{settings.database_schema}\""},
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para os modelos
Base = declarative_base()
Base.metadata.schema = settings.database_schema


def get_db():
    """
    Dependency que fornece uma sessão do banco de dados.
    Garante que a sessão seja fechada após o uso.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
