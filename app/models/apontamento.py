"""
Modelo SQLAlchemy para a entidade Apontamento (Registro de Horas).
"""

import uuid
import re
from datetime import datetime, date
from sqlalchemy import Column, String, DateTime, Date, Integer, ForeignKey
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

    # Duração no formato HH:mm (ex: "01:00", "02:30", "08:00")
    duracao = Column(
        String(5),
        nullable=False,
        comment="Duracao no formato HH:mm (ex: 01:00, 02:30)",
    )

    # Atividade relacionada (Tipo de Atividade: Documentação, Desenvolvimento, etc.)
    id_atividade = Column(
        GUID(),
        ForeignKey("atividades.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
        comment="ID da atividade associada (Tipo de Atividade)",
    )

    # Comentário opcional
    comentario = Column(
        String(500),
        nullable=True,
        comment="Comentario sobre o trabalho realizado (max 500 caracteres)",
    )

    # Dados do usuário que criou o apontamento (do Azure DevOps SDK)
    usuario_id = Column(
        String(255),
        nullable=False,
        index=True,
        comment="ID do usuario no Azure DevOps (IUserContext.id)",
    )

    usuario_nome = Column(
        String(255),
        nullable=False,
        comment="Nome de exibicao do usuario (IUserContext.displayName)",
    )

    usuario_email = Column(
        String(255),
        nullable=True,
        comment="Email do usuario (IUserContext.name)",
    )

    # Timestamps
    criado_em = Column(DateTime, default=datetime.utcnow, nullable=False)
    atualizado_em = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relacionamento com Atividade
    atividade = relationship("Atividade", lazy="joined")

    @property
    def duracao_horas(self) -> float:
        """Retorna a duracao em horas decimais (ex: 1.5 para 01:30)."""
        if not self.duracao:
            return 0.0
        match = re.match(r"^(\d{1,2}):(\d{2})$", self.duracao)
        if match:
            horas = int(match.group(1))
            minutos = int(match.group(2))
            return horas + (minutos / 60)
        return 0.0

    @property
    def duracao_minutos(self) -> int:
        """Retorna a duracao total em minutos."""
        if not self.duracao:
            return 0
        match = re.match(r"^(\d{1,2}):(\d{2})$", self.duracao)
        if match:
            horas = int(match.group(1))
            minutos = int(match.group(2))
            return (horas * 60) + minutos
        return 0

    def __repr__(self) -> str:
        return f"<Apontamento(id={self.id}, work_item={self.work_item_id}, duracao={self.duracao})>"
