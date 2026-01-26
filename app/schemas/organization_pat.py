"""
Schemas Pydantic para validação de dados de PATs por organização.
"""

from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict, field_validator


class OrganizationPatBase(BaseModel):
    """Schema base com campos comuns."""

    organization_name: str = Field(
        ..., 
        min_length=1, 
        max_length=255, 
        description="Nome da organização no Azure DevOps (ex: sefaz-ceara)"
    )
    organization_url: str | None = Field(
        default=None, 
        max_length=500,
        description="URL completa da organização (ex: https://dev.azure.com/sefaz-ceara)"
    )
    descricao: str | None = Field(
        default=None, 
        description="Descrição ou observação sobre o PAT"
    )
    expira_em: datetime | None = Field(
        default=None, 
        description="Data de expiração do PAT no Azure DevOps"
    )
    ativo: bool = Field(
        default=True, 
        description="Status ativo/inativo do PAT"
    )

    @field_validator("organization_name", mode="before")
    @classmethod
    def normalize_org_name(cls, v):
        """Normaliza o nome da organização para lowercase."""
        if isinstance(v, str):
            return v.lower().strip()
        return v
    
    @field_validator("organization_url", "descricao", mode="before")
    @classmethod
    def empty_string_to_none(cls, v):
        """Converte strings vazias para None."""
        if v == "" or v is None:
            return None
        return v
    
    @field_validator("expira_em", mode="before")
    @classmethod
    def parse_expira_em(cls, v):
        """Converte strings vazias para None e valida datas."""
        if v == "" or v is None:
            return None
        return v
    
    @field_validator("organization_url", mode="before")
    @classmethod
    def normalize_org_url(cls, v, info):
        """Gera URL automaticamente se não fornecida."""
        if not v and "organization_name" in info.data:
            org_name = info.data["organization_name"]
            if org_name:
                return f"https://dev.azure.com/{org_name}"
        return v


class OrganizationPatCreate(OrganizationPatBase):
    """Schema para criação de PAT de organização."""

    pat: str = Field(
        ..., 
        min_length=10,
        description="Personal Access Token do Azure DevOps (será criptografado)"
    )


class OrganizationPatUpdate(BaseModel):
    """Schema para atualização de PAT de organização."""

    organization_url: str | None = Field(
        default=None, 
        max_length=500,
        description="URL completa da organização"
    )
    descricao: str | None = Field(
        default=None, 
        description="Descrição ou observação sobre o PAT"
    )
    expira_em: datetime | None = Field(
        default=None, 
        description="Data de expiração do PAT no Azure DevOps"
    )
    ativo: bool | None = Field(
        default=None, 
        description="Status ativo/inativo do PAT"
    )
    pat: str | None = Field(
        default=None, 
        min_length=10,
        description="Novo PAT (se não fornecido, mantém o atual)"
    )


class OrganizationPatResponse(BaseModel):
    """Schema de resposta para PAT de organização."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(..., description="ID único do registro")
    organization_name: str = Field(..., description="Nome da organização")
    organization_url: str | None = Field(None, description="URL da organização")
    pat_masked: str | None = Field(None, description="PAT mascarado para exibição")
    descricao: str | None = Field(None, description="Descrição")
    expira_em: datetime | None = Field(None, description="Data de expiração")
    ativo: bool = Field(..., description="Status ativo")
    criado_por: str | None = Field(None, description="Quem criou")
    criado_em: datetime = Field(..., description="Data de criação")
    atualizado_em: datetime = Field(..., description="Data da última atualização")
    status_validacao: str | None = Field(
        None, 
        description="Status da validação do PAT (válido, inválido, não verificado)"
    )


class OrganizationPatList(BaseModel):
    """Schema para listagem de PATs."""

    items: list[OrganizationPatResponse] = Field(..., description="Lista de PATs")
    total: int = Field(..., description="Total de registros")


class OrganizationPatValidateRequest(BaseModel):
    """Schema para validação de PAT."""

    organization_name: str = Field(..., description="Nome da organização")
    pat: str = Field(..., description="PAT a ser validado")


class OrganizationPatValidateResponse(BaseModel):
    """Schema de resposta da validação de PAT."""

    valid: bool = Field(..., description="Se o PAT é válido")
    organization_name: str = Field(..., description="Nome da organização")
    message: str = Field(..., description="Mensagem de resultado")
    projects_count: int | None = Field(None, description="Número de projetos encontrados")
    projects: list[str] | None = Field(None, description="Nomes dos projetos encontrados")
