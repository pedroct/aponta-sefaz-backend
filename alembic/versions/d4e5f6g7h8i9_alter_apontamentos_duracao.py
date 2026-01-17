"""Alter apontamentos: replace horas/minutos with duracao

Revision ID: d4e5f6g7h8i9
Revises: c3d4e5f6g7h8
Create Date: 2026-01-17 20:00:00.000000

This migration changes the time tracking from separate horas/minutos fields
to a single duracao field in HH:mm format.
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'd4e5f6g7h8i9'
down_revision: Union[str, None] = 'c3d4e5f6g7h8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add new duracao column
    op.add_column(
        'apontamentos',
        sa.Column(
            'duracao',
            sa.String(5),
            nullable=True,
            comment='Duracao no formato HH:mm (ex: 01:00, 02:30)'
        ),
        schema='api_aponta'
    )

    # Migrate existing data: convert horas/minutos to duracao format
    op.execute("""
        UPDATE api_aponta.apontamentos
        SET duracao = LPAD(horas::text, 2, '0') || ':' || LPAD(minutos::text, 2, '0')
    """)

    # Make duracao NOT NULL after migration
    op.alter_column(
        'apontamentos',
        'duracao',
        nullable=False,
        schema='api_aponta'
    )

    # Drop old columns
    op.drop_column('apontamentos', 'horas', schema='api_aponta')
    op.drop_column('apontamentos', 'minutos', schema='api_aponta')

    # Increase comentario max length from 100 to 500
    op.alter_column(
        'apontamentos',
        'comentario',
        type_=sa.String(500),
        existing_type=sa.String(100),
        existing_nullable=True,
        schema='api_aponta'
    )


def downgrade() -> None:
    # Re-add horas and minutos columns
    op.add_column(
        'apontamentos',
        sa.Column('horas', sa.Integer(), nullable=True, comment='Quantidade de horas trabalhadas (0-8)'),
        schema='api_aponta'
    )
    op.add_column(
        'apontamentos',
        sa.Column('minutos', sa.Integer(), nullable=True, comment='Quantidade de minutos trabalhados (0, 15, 30, 45)'),
        schema='api_aponta'
    )

    # Migrate data back: extract hours and minutes from duracao
    op.execute("""
        UPDATE api_aponta.apontamentos
        SET horas = CAST(SPLIT_PART(duracao, ':', 1) AS INTEGER),
            minutos = CAST(SPLIT_PART(duracao, ':', 2) AS INTEGER)
    """)

    # Make columns NOT NULL
    op.alter_column('apontamentos', 'horas', nullable=False, schema='api_aponta')
    op.alter_column('apontamentos', 'minutos', nullable=False, schema='api_aponta')

    # Drop duracao column
    op.drop_column('apontamentos', 'duracao', schema='api_aponta')

    # Revert comentario max length
    op.alter_column(
        'apontamentos',
        'comentario',
        type_=sa.String(100),
        existing_type=sa.String(500),
        existing_nullable=True,
        schema='api_aponta'
    )
