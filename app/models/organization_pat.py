"""
Modelo SQLAlchemy para armazenar PATs por organização Azure DevOps.
"""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, Boolean, DateTime
from sqlalchemy.orm import validates
from app.models.custom_types import GUID
from app.database import Base
from cryptography.fernet import Fernet
from app.config import get_settings


def get_cipher():
    """Retorna o cipher para criptografia do PAT."""
    settings = get_settings()
    # Usa uma chave derivada do secret key ou uma chave específica
    key = settings.pat_encryption_key
    if not key:
        # Gera uma chave baseada no secret (para retrocompatibilidade)
        import hashlib
        import base64
        hash_key = hashlib.sha256(settings.secret_key.encode()).digest()
        key = base64.urlsafe_b64encode(hash_key)
    return Fernet(key)


class OrganizationPat(Base):
    """Modelo para armazenar PATs de organizações Azure DevOps."""

    __tablename__ = "organization_pats"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4, index=True)
    
    # Nome da organização (ex: sefaz-ceara, sefaz-ce-siscoex2)
    organization_name = Column(
        String(255), 
        nullable=False, 
        unique=True, 
        index=True,
        comment="Nome da organização no Azure DevOps"
    )
    
    # URL base da organização (ex: https://dev.azure.com/sefaz-ceara)
    organization_url = Column(
        String(500),
        nullable=True,
        comment="URL completa da organização"
    )
    
    # PAT criptografado
    pat_encrypted = Column(
        Text,
        nullable=False,
        comment="PAT criptografado com Fernet"
    )
    
    # Descrição/observação
    descricao = Column(
        Text,
        nullable=True,
        comment="Descrição ou observação sobre o PAT"
    )
    
    # Data de expiração do PAT (informativo)
    expira_em = Column(
        DateTime,
        nullable=True,
        comment="Data de expiração do PAT no Azure DevOps"
    )
    
    # Status ativo
    ativo = Column(Boolean, default=True, nullable=False)
    
    # Audit fields
    criado_por = Column(
        String(255),
        nullable=True,
        index=True,
        comment="Email do usuário que criou o registro"
    )
    criado_em = Column(DateTime, default=datetime.utcnow, nullable=False)
    atualizado_em = Column(
        DateTime, 
        default=datetime.utcnow, 
        onupdate=datetime.utcnow, 
        nullable=False
    )
    
    @validates('organization_name')
    def validate_organization_name(self, key, value):
        """Normaliza o nome da organização para lowercase."""
        if value:
            return value.lower().strip()
        return value
    
    def set_pat(self, pat_plain: str):
        """Criptografa e armazena o PAT."""
        cipher = get_cipher()
        self.pat_encrypted = cipher.encrypt(pat_plain.encode()).decode()
    
    def get_pat(self) -> str:
        """Descriptografa e retorna o PAT."""
        if not self.pat_encrypted:
            return None
        cipher = get_cipher()
        return cipher.decrypt(self.pat_encrypted.encode()).decode()
    
    @property
    def pat_masked(self) -> str:
        """Retorna o PAT mascarado para exibição."""
        pat = self.get_pat()
        if not pat:
            return None
        if len(pat) <= 10:
            return "*" * len(pat)
        return pat[:4] + "*" * (len(pat) - 8) + pat[-4:]
    
    def __repr__(self):
        return f"<OrganizationPat(organization={self.organization_name}, ativo={self.ativo})>"
