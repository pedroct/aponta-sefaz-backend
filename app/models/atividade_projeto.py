"""
Modelo SQLAlchemy para a tabela de junção AtividadeProjeto (N:N).
"""

import uuid
from datetime import datetime
from sqlalchemy import Column, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.models.custom_types import GUID
from app.database import Base


class AtividadeProjeto(Base):
    """Modelo da tabela de junção atividade_projeto para relação N:N."""

    __tablename__ = "atividade_projeto"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    id_atividade = Column(
        GUID(),
        ForeignKey("atividades.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    id_projeto = Column(
        GUID(),
        ForeignKey("projetos.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    criado_em = Column(DateTime, default=datetime.utcnow, nullable=False)

    __table_args__ = (
        UniqueConstraint("id_atividade", "id_projeto", name="uq_atividade_projeto"),
    )

    # Relationships
    atividade = relationship("Atividade", back_populates="atividade_projetos")
    projeto = relationship("Projeto", back_populates="atividade_projetos")

    def __repr__(self) -> str:
        return f"<AtividadeProjeto(atividade={self.id_atividade}, projeto={self.id_projeto})>"
