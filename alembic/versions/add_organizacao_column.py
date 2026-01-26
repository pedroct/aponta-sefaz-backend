"""Add organizacao column to projetos table

Revision ID: add_organizacao_col
Revises: d4e5f6g7h8i9
Create Date: 2026-01-26 00:45:00.000000

"""
from typing import Sequence, Union
import os
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'add_organizacao_col'
down_revision: Union[str, None] = 'd4e5f6g7h8i9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Get schema from environment
SCHEMA = os.getenv("DATABASE_SCHEMA", "public")


def upgrade() -> None:
    # Add organizacao column to projetos table
    op.add_column('projetos', sa.Column('organizacao', sa.String(), nullable=True, comment='Nome da organização do Azure DevOps'), schema=SCHEMA)
    op.create_index(op.f('ix_projetos_organizacao'), 'projetos', ['organizacao'], unique=False, schema=SCHEMA)


def downgrade() -> None:
    op.drop_index(op.f('ix_projetos_organizacao'), table_name='projetos', schema=SCHEMA)
    op.drop_column('projetos', 'organizacao', schema=SCHEMA)
