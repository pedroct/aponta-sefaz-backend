"""
Utilitário para normalizar project_id.

Durante a transição, aceita tanto nome do projeto quanto UUID,
convertendo automaticamente para UUID quando necessário.
"""

import re
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import text


def is_valid_uuid(value: str) -> bool:
    """
    Verifica se uma string é um UUID válido.
    
    Args:
        value: String para validar
        
    Returns:
        True se for um UUID válido, False caso contrário
    """
    if value is None:
        return False
    try:
        UUID(value)
        return True
    except (ValueError, AttributeError, TypeError):
        return False


def normalize_project_id(project_id: str, db: Session) -> str:
    """
    Normaliza project_id para UUID.
    
    Durante a transição, aceita:
    - UUID válido: retorna como está
    - Nome do projeto: busca o UUID correspondente na tabela projetos
    
    Args:
        project_id: ID do projeto (UUID ou nome)
        db: Sessão do banco de dados
        
    Returns:
        UUID do projeto como string
        
    Raises:
        ValueError: Se o projeto não for encontrado ou se o formato for inválido
    """
    # Se já é um UUID válido, retorna como está
    if is_valid_uuid(project_id):
        return project_id
    
    # Se não é UUID, assume que é um nome e busca na tabela projetos
    # Remove espaços extras
    project_name = project_id.strip()
    
    if not project_name:
        raise ValueError("project_id não pode ser vazio")
    
    # Busca o UUID do projeto pelo nome (case-insensitive)
    result = db.execute(
        text("""
            SELECT CAST(external_id AS TEXT)
            FROM projetos 
            WHERE UPPER(nome) = UPPER(:project_name)
            LIMIT 1
        """),
        {"project_name": project_name}
    )
    
    row = result.fetchone()
    
    if not row:
        raise ValueError(
            f"Projeto '{project_name}' não encontrado. "
            f"Por favor, use o UUID do projeto (IProjectInfo.id) "
            f"ou verifique se o projeto existe na tabela 'projetos'."
        )
    
    project_uuid = row[0]
    
    return project_uuid


def validate_project_id_format(project_id: str) -> str:
    """
    Valida apenas o formato do project_id (UUID válido).
    
    Use esta função quando você quer validar sem acesso ao banco de dados.
    Para normalização completa (aceitar nome), use normalize_project_id().
    
    Args:
        project_id: ID do projeto para validar
        
    Returns:
        O mesmo project_id se for válido
        
    Raises:
        ValueError: Se não for um UUID válido
    """
    project_id = project_id.strip()
    
    if not project_id:
        raise ValueError("project_id não pode ser vazio")
    
    if not is_valid_uuid(project_id):
        raise ValueError(
            f"project_id deve ser um UUID válido. "
            f"Recebido: '{project_id}'. "
            f"Formato esperado: '50a9ca09-710f-4478-8278-2d069902d2af'"
        )
    
    return project_id
