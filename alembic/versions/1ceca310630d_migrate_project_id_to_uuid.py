"""migrate_project_id_to_uuid

Revision ID: 1ceca310630d
Revises: d4e5f6g7h8i9
Create Date: 2026-01-25 17:27:33.871672

Migra os registros antigos de apontamentos que possuem project_id como string (ex: "DEV")
para o formato UUID correto, buscando na tabela projetos pelo nome.

Esta migração é necessária porque:
1. A tela Gestão de Apontamentos enviava o nome do projeto ("DEV")
2. O novo Modal do Work Item envia o UUID do projeto ("50a9ca09-710f-4478-8278-2d069902d2af")
3. Precisamos normalizar todos os registros para usar UUID

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy import text
import os


# revision identifiers, used by Alembic.
revision: str = '1ceca310630d'
down_revision: Union[str, None] = 'add_organizacao_col'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Migra project_id de nome para UUID.
    
    Estratégia:
    1. Busca todos os apontamentos com project_id que não são UUID (não contém hífens)
    2. Para cada um, busca o UUID correspondente na tabela projetos pelo nome
    3. Atualiza o project_id com o UUID correto
    """
    conn = op.get_bind()
    
    # Obter o schema correto das configurações (default: public)
    schema = os.getenv('DATABASE_SCHEMA', 'public')
    
    # Verifica se a tabela apontamentos existe no schema correto
    table_check = conn.execute(text("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_schema = :schema
            AND table_name = 'apontamentos'
        )
    """), {"schema": schema})
    
    table_exists = table_check.scalar()
    
    if not table_exists:
        print(f"⚠️  Tabela '{schema}.apontamentos' não existe ainda. Pulando migração de dados.")
        print("    Esta migração será executada automaticamente quando a tabela for criada.")
        return
    
    # Primeiro, verifica se há registros para migrar
    result = conn.execute(text(f"""
        SELECT DISTINCT project_id 
        FROM {schema}.apontamentos 
        WHERE project_id NOT LIKE '%-%'
        AND LENGTH(project_id) < 36
    """))
    
    project_names = [row[0] for row in result]
    
    if not project_names:
        print("✓ Nenhum registro para migrar. Todos os project_id já estão no formato UUID.")
        return
    
    print(f"Encontrados {len(project_names)} project_id(s) no formato antigo: {project_names}")
    
    # Para cada nome de projeto, busca o UUID e atualiza
    migrated_count = 0
    not_found = []
    
    for project_name in project_names:
        # Busca o UUID do projeto pelo nome na tabela projetos
        uuid_result = conn.execute(text(f"""
            SELECT CAST(external_id AS TEXT)
            FROM {schema}.projetos 
            WHERE UPPER(nome) = UPPER(:project_name)
            LIMIT 1
        """), {"project_name": project_name})
        
        uuid_row = uuid_result.fetchone()
        
        if uuid_row:
            project_uuid = uuid_row[0]
            
            # Atualiza todos os apontamentos com este nome para o UUID correto
            update_result = conn.execute(text(f"""
                UPDATE {schema}.apontamentos 
                SET project_id = :project_uuid
                WHERE project_id = :project_name
            """), {"project_uuid": project_uuid, "project_name": project_name})
            
            updated_rows = update_result.rowcount
            migrated_count += updated_rows
            print(f"✓ Migrado '{project_name}' → '{project_uuid}' ({updated_rows} registros)")
        else:
            not_found.append(project_name)
            print(f"⚠ Projeto '{project_name}' não encontrado na tabela projetos")
    
    print(f"\n=== Resumo da Migração ===")
    print(f"Total de registros migrados: {migrated_count}")
    
    if not_found:
        print(f"\n⚠ ATENÇÃO: {len(not_found)} projeto(s) não encontrado(s):")
        for name in not_found:
            print(f"  - {name}")
        print("\nEstes registros não foram migrados. Você pode:")
        print("1. Adicionar manualmente os projetos na tabela 'projetos'")
        print("2. Atualizar manualmente os project_id destes apontamentos")
        print("3. Ou deletar estes registros se não forem mais necessários")


def downgrade() -> None:
    """
    Reverte a migração, convertendo UUID de volta para nome do projeto.
    
    ATENÇÃO: Esta operação pode resultar em perda de informação se houver
    múltiplos projetos com UUIDs diferentes mas mesmo nome.
    """
    conn = op.get_bind()
    
    print("Revertendo migração de project_id...")
    
    # Busca todos os UUIDs distintos nos apontamentos
    result = conn.execute(text("""
        SELECT DISTINCT project_id 
        FROM apontamentos 
        WHERE project_id LIKE '%-%'
        AND LENGTH(project_id) >= 36
    """))
    
    project_uuids = [row[0] for row in result]
    
    if not project_uuids:
        print("✓ Nenhum registro para reverter.")
        return
    
    print(f"Encontrados {len(project_uuids)} project_id(s) no formato UUID")
    
    reverted_count = 0
    
    for project_uuid in project_uuids:
        # Busca o nome do projeto pelo UUID
        name_result = conn.execute(text("""
            SELECT nome
            FROM projetos 
            WHERE CAST(external_id AS TEXT) = :project_uuid
            LIMIT 1
        """), {"project_uuid": project_uuid})
        
        name_row = name_result.fetchone()
        
        if name_row:
            project_name = name_row[0]
            
            # Reverte todos os apontamentos com este UUID para o nome
            update_result = conn.execute(text("""
                UPDATE apontamentos 
                SET project_id = :project_name
                WHERE project_id = :project_uuid
            """), {"project_name": project_name, "project_uuid": project_uuid})
            
            updated_rows = update_result.rowcount
            reverted_count += updated_rows
            print(f"✓ Revertido '{project_uuid}' → '{project_name}' ({updated_rows} registros)")
        else:
            print(f"⚠ Projeto com UUID '{project_uuid}' não encontrado na tabela projetos")
    
    print(f"\nTotal de registros revertidos: {reverted_count}")
