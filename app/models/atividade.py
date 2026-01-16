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
    criado_por = Column(
        String(255),
        nullable=True,
        index=True,
        comment="Email ou ID do usuário que criou a atividade",
    )
    criado_em = Column(DateTime, default=datetime.utcnow, nullable=False)
    atualizado_em = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relacionamento N:N com projetos através da tabela de junção
    atividade_projetos = relationship(
        "AtividadeProjeto",
        back_populates="atividade",
        cascade="all, delete-orphan",
        lazy="joined",
    )

    @property
    def projetos(self) -> list:
        """Retorna a lista de projetos associados à atividade."""
        return [ap.projeto for ap in self.atividade_projetos if ap.projeto]

    @property
    def nome_projeto(self) -> str | None:
        """Retorna o nome do primeiro projeto associado (retrocompatibilidade)."""
        if self.atividade_projetos and self.atividade_projetos[0].projeto:
            return self.atividade_projetos[0].projeto.nome
        return None

    @property
    def id_projeto(self) -> uuid.UUID | None:
        """Retorna o ID do primeiro projeto associado (retrocompatibilidade)."""
        if self.atividade_projetos:
            return self.atividade_projetos[0].id_projeto
        return None

    def __repr__(self) -> str:
        return f"<Atividade(id={self.id}, nome='{self.nome}')>"
