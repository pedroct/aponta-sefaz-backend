"""
Configurações da aplicação via variáveis de ambiente.
"""

from pydantic import Field, AliasChoices
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    """Configurações da aplicação."""

    # Supabase (opcional em desenvolvimento)
    supabase_url: str = Field("", validation_alias=AliasChoices("SUPABASE_URL", "supabase_url"))
    supabase_key: str = Field("", validation_alias=AliasChoices("SUPABASE_KEY", "supabase_key"))
    supabase_service_role_key: str = Field(
        "", validation_alias=AliasChoices("SUPABASE_SERVICE_ROLE_KEY", "supabase_service_role_key")
    )

    # Banco de Dados (pode ser Supabase ou local)
    database_url: str = Field(
        "", validation_alias=AliasChoices("DATABASE_URL", "database_url")
    )
    database_host: str = "localhost"
    database_port: int = 5432
    database_name: str = "gestao_projetos"
    database_user: str = "postgres"
    database_password: str = "postgres"

    # Usamos Field com alias para garantir compatibilidade com diferentes cases
    # Padrão é aponta_sefaz (produção)
    database_schema: str = Field(
        "aponta_sefaz", validation_alias=AliasChoices("DATABASE_SCHEMA", "database_schema")
    )

    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_debug: bool = False
    api_title: str = "API Aponta Supabase"
    api_version: str = "0.1.0"

    # Ambiente
    environment: str = "development"

    # Seed
    seed_initial_data: bool = Field(
        default=True,
        validation_alias=AliasChoices("SEED_INITIAL_DATA", "seed_initial_data"),
    )

    # CORS
    cors_origins: str = "http://localhost:3000,http://localhost:5173"

    # Autenticação Azure DevOps
    auth_enabled: bool = True
    azure_devops_org_url: str = ""
    azure_devops_pat: str = ""
    
    # PATs para organizações adicionais (formato: org1=pat1,org2=pat2)
    # Exemplo: AZURE_DEVOPS_ORG_PATS="sefaz-ce-diligencia=xxx,sefaz-ce-siscoex2=yyy"
    azure_devops_org_pats: str = Field(
        "", validation_alias=AliasChoices("AZURE_DEVOPS_ORG_PATS", "azure_devops_org_pats")
    )
    
    # Secret da extensão Azure DevOps (para validar App Tokens JWT)
    # Obter em: https://aka.ms/vsmarketplace-manage > Botão direito > Certificate
    azure_extension_secret: str = Field(
        "", validation_alias=AliasChoices("AZURE_EXTENSION_SECRET", "azure_extension_secret")
    )
    
    # Chave para criptografia de PATs no banco de dados (Fernet key - 32 bytes base64)
    # Gerar com: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
    pat_encryption_key: str = Field(
        "", validation_alias=AliasChoices("PAT_ENCRYPTION_KEY", "pat_encryption_key")
    )
    
    # Secret key para geração de chave de criptografia (fallback)
    secret_key: str = Field(
        "aponta-sefaz-secret-key-change-in-production",
        validation_alias=AliasChoices("SECRET_KEY", "secret_key")
    )
    azure_extension_app_id: str = Field(
        "560de67c-a2e8-408a-86ae-be7ea6bd0b7a",  # App ID da extensão
        validation_alias=AliasChoices("AZURE_EXTENSION_APP_ID", "azure_extension_app_id")
    )
    
    def get_pat_for_org(self, org_name: str) -> str:
        """Retorna o PAT para uma organização específica."""
        # Primeiro, verifica se há PAT específico na lista de org_pats
        if self.azure_devops_org_pats:
            for mapping in self.azure_devops_org_pats.split(","):
                if "=" in mapping:
                    org, pat = mapping.strip().split("=", 1)
                    if org.strip().lower() == org_name.lower():
                        return pat.strip()
        
        # Fallback: retorna o PAT padrão
        return self.azure_devops_pat
    
    def get_all_organizations(self) -> list[dict]:
        """Retorna lista de todas as organizações configuradas com seus PATs."""
        import re
        organizations = []
        
        # Organização principal (da AZURE_DEVOPS_ORG_URL)
        if self.azure_devops_org_url and self.azure_devops_pat:
            match = re.search(r"dev\.azure\.com/([^/]+)", self.azure_devops_org_url)
            if match:
                main_org = match.group(1)
                organizations.append({
                    "name": main_org,
                    "pat": self.azure_devops_pat,
                    "url": self.azure_devops_org_url,
                })
        
        # Organizações adicionais (de AZURE_DEVOPS_ORG_PATS)
        if self.azure_devops_org_pats:
            for mapping in self.azure_devops_org_pats.split(","):
                if "=" in mapping:
                    org, pat = mapping.strip().split("=", 1)
                    org = org.strip()
                    pat = pat.strip()
                    if org and pat:
                        organizations.append({
                            "name": org,
                            "pat": pat,
                            "url": f"https://dev.azure.com/{org}",
                        })
        
        return organizations

    # GitHub
    github_token: str = ""
    github_repo: str = ""

    @property
    def cors_origins_list(self) -> list[str]:
        """Retorna lista de origens CORS permitidas."""
        origins = [origin.strip() for origin in self.cors_origins.split(",")]

        # Remove wildcards que não funcionam no CORS do FastAPI
        origins = [o for o in origins if not o.startswith("https://*.")]

        # Adiciona origens conhecidas do Azure DevOps
        azure_devops_origins = [
            "https://dev.azure.com",
            "https://sefaz-ceara.gallerycdn.vsassets.io",
            "https://sefaz-ceara-lab.gallerycdn.vsassets.io",
            "https://vsassets.io",
        ]

        # Frontend em produção
        frontend_origins = [
            "https://aponta.pedroct.com.br",
            "http://aponta.pedroct.com.br",
        ]

        # Adiciona origens localhost comuns para desenvolvimento
        dev_origins = [
            "http://localhost",
            "http://127.0.0.1",
            "http://localhost:80",
            "http://127.0.0.1:80",
            "http://localhost:8082",
            "http://127.0.0.1:8082",
            "http://localhost:5000",
            "http://127.0.0.1:5000",
            "http://localhost:5002",
            "http://127.0.0.1:5002",
            "http://localhost:3000",
            "http://127.0.0.1:3000",
            "http://localhost:5173",
            "http://127.0.0.1:5173",
        ]

        # Adiciona todas as origens que não existem
        for origin in azure_devops_origins + frontend_origins + dev_origins:
            if origin not in origins:
                origins.append(origin)

        return origins

    @property
    def database_url_resolved(self) -> str:
        """Retorna a URL de conexão com o banco de dados."""
        if self.database_url:
            return self.database_url
        return (
            f"postgresql://{self.database_user}:{self.database_password}"
            f"@{self.database_host}:{self.database_port}/{self.database_name}"
        )

    @property
    def database_url_legacy(self) -> str:
        """Retorna a URL de conexão com o banco de dados (formato legado)."""
        return (
            f"postgresql://{self.database_user}:{self.database_password}"
            f"@{self.database_host}:{self.database_port}/{self.database_name}"
        )

    model_config = SettingsConfigDict(
        extra="ignore",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


@lru_cache
def get_settings() -> Settings:
    """Retorna instância singleton das configurações."""
    return Settings()
