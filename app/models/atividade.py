"""
Modelo SQLAlchemy para a entidade Atividade.
"""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, Boolean, DateTime
from app.models.custom_types import GUID
from sqlalchemy.orm import relationship
from app.database import Base


class Atividade(Base):
    """Modelo da tabela atividades."""

    __tablename__ = "atividades"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4, index=True)
    nome = Column(String(255), nullable=False, index=True)
    descricao = Column(Text, nullable=True)
    ativo = Column(Boolean, default=True, nullable=False)
    # ID do projeto no Azure Boards
    # Preenchido via Azure DevOps Web Extension SDK
    id_projeto = Column(
        GUID(),
        nullable=False,
        index=True,
        comment="Project ID from Azure Boards (Azure DevOps)",
    )
    criado_em = Column(DateTime, default=datetime.utcnow, nullable=False)
    atualizado_em = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relacionamento com o projeto (baseado no id interno do projeto)
    projeto = relationship(
        "Projeto",
        primaryjoin="Atividade.id_projeto == Projeto.external_id",
        foreign_keys="[Atividade.id_projeto]",
        uselist=False,
        viewonly=True,
        lazy="joined",
    )

    @property
    def nome_projeto(self) -> str | None:
        """Retorna o nome do projeto associado, se existir."""
        return self.projeto.nome if self.projeto else None

    def __repr__(self) -> str:
        return f"<Atividade(id={self.id}, nome='{self.nome}')>"
