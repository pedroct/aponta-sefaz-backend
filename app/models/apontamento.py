"""
Modelo SQLAlchemy para a entidade Apontamento (Registro de Horas).
"""

import uuid
from datetime import datetime, date
from sqlalchemy import Column, String, Text, DateTime, Date, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.models.custom_types import GUID
from app.database import Base


class Apontamento(Base):
    """Modelo da tabela apontamentos (registro de horas trabalhadas)."""

    __tablename__ = "apontamentos"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4, index=True)

    # Work Item do Azure DevOps
    work_item_id = Column(
        Integer,
        nullable=False,
        index=True,
        comment="ID do Work Item no Azure DevOps",
    )

    # Projeto do Azure DevOps
    project_id = Column(
        String(255),
        nullable=False,
        index=True,
        comment="ID do projeto no Azure DevOps (IProjectInfo.id)",
    )

    # Organização do Azure DevOps
    organization_name = Column(
        String(255),
        nullable=False,
        index=True,
        comment="Nome da organização no Azure DevOps (IHostContext.name)",
    )

    # Data do apontamento
    data_apontamento = Column(
        Date,
        nullable=False,
        index=True,
        comment="Data em que o trabalho foi realizado",
    )

    # Horas trabalhadas (0-8)
    horas = Column(
        Integer,
        nullable=False,
        comment="Quantidade de horas trabalhadas (0-8)",
    )

    # Minutos trabalhados (00, 15, 30, 45)
    minutos = Column(
        Integer,
        nullable=False,
        comment="Quantidade de minutos trabalhados (0, 15, 30, 45)",
    )

    # Atividade relacionada
    id_atividade = Column(
        GUID(),
        ForeignKey("atividades.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
        comment="ID da atividade associada",
    )

    # Comentário opcional
    comentario = Column(
        String(100),
        nullable=True,
        comment="Comentário sobre o trabalho realizado (máx 100 caracteres)",
    )

    # Dados do usuário que criou o apontamento (do Azure DevOps SDK)
    usuario_id = Column(
        String(255),
        nullable=False,
        index=True,
        comment="ID do usuário no Azure DevOps (IUserContext.id)",
    )

    usuario_nome = Column(
        String(255),
        nullable=False,
        comment="Nome de exibição do usuário (IUserContext.displayName)",
    )

    usuario_email = Column(
        String(255),
        nullable=True,
        comment="Nome de login do usuário (IUserContext.name)",
    )

    # Timestamps
    criado_em = Column(DateTime, default=datetime.utcnow, nullable=False)
    atualizado_em = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relacionamento com Atividade
    atividade = relationship("Atividade", lazy="joined")

    @property
    def tempo_total_minutos(self) -> int:
        """Retorna o tempo total em minutos."""
        return (self.horas * 60) + self.minutos

    @property
    def tempo_formatado(self) -> str:
        """Retorna o tempo formatado como HH:MM."""
        return f"{self.horas:02d}:{self.minutos:02d}"

    def __repr__(self) -> str:
        return f"<Apontamento(id={self.id}, work_item={self.work_item_id}, tempo={self.tempo_formatado})>"
