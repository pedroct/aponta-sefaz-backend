"""cleanup_old_schemas

Revision ID: cleanup_old_1234567890
Revises: d4e5f6g7h8i9
Create Date: 2026-01-22 15:30:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


revision: str = 'cleanup_old_1234567890'
down_revision: Union[str, None] = 'd4e5f6g7h8i9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Remove schemas antigos e qualquer dado em public.
    Garante limpeza total de schemas indevidos.
    """
    bind = op.get_bind()
    
    # Remover schemas antigos se existirem
    try:
        bind.execute(sa.text("DROP SCHEMA IF EXISTS api_aponta CASCADE"))
        print("✅ Schema api_aponta removido")
    except Exception as e:
        print(f"⚠️  Não foi possível remover api_aponta: {e}")
    
    try:
        bind.execute(sa.text("DROP SCHEMA IF EXISTS api_aponta_staging CASCADE"))
        print("✅ Schema api_aponta_staging removido")
    except Exception as e:
        print(f"⚠️  Não foi possível remover api_aponta_staging: {e}")
    
    # Remover tabelas de aplicação do schema public (deixar apenas as do postgres)
    try:
        # Listar todas as tabelas no schema public que não são do postgres
        result = bind.execute(sa.text(
            "SELECT tablename FROM pg_tables "
            "WHERE schemaname = 'public' AND tablename NOT LIKE 'pg_%' AND tablename NOT LIKE 'sql_%'"
        ))
        
        for row in result:
            table_name = row[0]
            try:
                bind.execute(sa.text(f'DROP TABLE IF EXISTS public."{table_name}" CASCADE'))
                print(f"✅ Tabela public.{table_name} removida")
            except Exception as e:
                print(f"⚠️  Não foi possível remover public.{table_name}: {e}")
    except Exception as e:
        print(f"⚠️  Erro ao listar tabelas do public: {e}")
    
    # Remover sequências do schema public que não são do postgres
    try:
        result = bind.execute(sa.text(
            "SELECT sequence_name FROM information_schema.sequences "
            "WHERE sequence_schema = 'public' AND sequence_name NOT LIKE 'pg_%' AND sequence_name NOT LIKE 'sql_%'"
        ))
        
        for row in result:
            seq_name = row[0]
            try:
                bind.execute(sa.text(f'DROP SEQUENCE IF EXISTS public."{seq_name}" CASCADE'))
                print(f"✅ Sequência public.{seq_name} removida")
            except Exception as e:
                print(f"⚠️  Não foi possível remover public.{seq_name}: {e}")
    except Exception as e:
        print(f"⚠️  Erro ao listar sequências do public: {e}")


def downgrade() -> None:
    """
    Downgrade não é suportado para este tipo de limpeza.
    As mudanças são irreversíveis.
    """
    pass
