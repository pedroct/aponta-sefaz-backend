"""
Cliente Supabase para integração com o banco de dados.
"""
from typing import Optional
from supabase import create_client, Client
from app.config import get_settings

settings = get_settings()


class SupabaseClient:
    """Cliente singleton para Supabase."""

    _instance: Optional[Client] = None

    @classmethod
    def get_client(cls) -> Client:
        """
        Retorna uma instância do cliente Supabase.

        Returns:
            Client: Instância do cliente Supabase
        """
        if cls._instance is None:
            cls._instance = create_client(
                supabase_url=settings.SUPABASE_URL,
                supabase_key=settings.SUPABASE_KEY,
            )
        return cls._instance

    @classmethod
    def get_admin_client(cls) -> Client:
        """
        Retorna uma instância do cliente Supabase com privilégios administrativos.

        Returns:
            Client: Instância do cliente Supabase com service role key
        """
        return create_client(
            supabase_url=settings.SUPABASE_URL,
            supabase_key=settings.SUPABASE_SERVICE_ROLE_KEY,
        )


def get_supabase() -> Client:
    """
    Dependency injection para obter o cliente Supabase.

    Returns:
        Client: Instância do cliente Supabase
    """
    return SupabaseClient.get_client()


def get_supabase_admin() -> Client:
    """
    Dependency injection para obter o cliente Supabase administrativo.

    Returns:
        Client: Instância do cliente Supabase com privilégios administrativos
    """
    return SupabaseClient.get_admin_client()
