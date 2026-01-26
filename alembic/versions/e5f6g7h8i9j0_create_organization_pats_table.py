"""Create organization_pats table

Revision ID: e5f6g7h8i9j0
Revises: add_organizacao_col
Create Date: 2026-01-26

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import sys
import os

# Adicionar o diretório raiz ao path para importar app.config
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.config import get_settings

# revision identifiers, used by Alembic.
revision: str = 'e5f6g7h8i9j0'
down_revision: Union[str, None] = 'add_organizacao_col'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Obter o schema dinamicamente
settings = get_settings()
DB_SCHEMA = settings.database_schema


def upgrade() -> None:
    op.create_table(
        'organization_pats',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('organization_name', sa.String(255), nullable=False, unique=True, index=True),
        sa.Column('organization_url', sa.String(500), nullable=True),
        sa.Column('pat_encrypted', sa.Text(), nullable=False),
        sa.Column('descricao', sa.Text(), nullable=True),
        sa.Column('expira_em', sa.DateTime(), nullable=True),
        sa.Column('ativo', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('criado_por', sa.String(255), nullable=True, index=True),
        sa.Column('criado_em', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('atualizado_em', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('organization_name'),
        schema=DB_SCHEMA
    )
    
    # Criar índice para busca por organização
    op.create_index('ix_organization_pats_organization_name', 'organization_pats', ['organization_name'], schema=DB_SCHEMA)
    op.create_index('ix_organization_pats_criado_por', 'organization_pats', ['criado_por'], schema=DB_SCHEMA)


def downgrade() -> None:
    op.drop_index('ix_organization_pats_criado_por', table_name='organization_pats', schema=DB_SCHEMA)
    op.drop_index('ix_organization_pats_organization_name', table_name='organization_pats', schema=DB_SCHEMA)
    op.drop_table('organization_pats', schema=DB_SCHEMA)
