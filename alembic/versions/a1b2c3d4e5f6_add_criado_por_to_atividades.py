"""add criado_por column to atividades

Revision ID: a1b2c3d4e5f6
Revises: 90324eefb107
Create Date: 2026-01-13 10:50:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, None] = '90324eefb107'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add criado_por column to atividades table
    op.add_column(
        'atividades',
        sa.Column(
            'criado_por',
            sa.String(length=255),
            nullable=True,
            comment='Email ou ID do usuário que criou a atividade'
        ),
        schema='api_aponta'
    )
    # Create index for criado_por column
    op.create_index(
        op.f('ix_api_aponta_atividades_criado_por'),
        'atividades',
        ['criado_por'],
        unique=False,
        schema='api_aponta'
    )


def downgrade() -> None:
    # Remove index and column
    op.drop_index(
        op.f('ix_api_aponta_atividades_criado_por'),
        table_name='atividades',
        schema='api_aponta'
    )
    op.drop_column('atividades', 'criado_por', schema='api_aponta')
