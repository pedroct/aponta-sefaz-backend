from sqlalchemy import Column, String, DateTime, Text
from app.models.custom_types import GUID
import uuid
from sqlalchemy.sql import func
from app.database import Base


class Projeto(Base):
    __tablename__ = "projetos"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    external_id = Column(
        GUID(),
        unique=True,
        index=True,
        nullable=False,
        comment="ID do projeto no Azure DevOps",
    )
    nome = Column(String, nullable=False, index=True)
    descricao = Column(Text, nullable=True)
    url = Column(String, nullable=True)
    estado = Column(
        String, nullable=True, comment="Estado do projeto (wellFormed, deleting, etc)"
    )
    last_sync_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        comment="Data da última sincronização",
    )

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
