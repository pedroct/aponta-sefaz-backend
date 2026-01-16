"""Add N:N relation between atividades and projetos

Revision ID: b2c3d4e5f6g7
Revises: a1b2c3d4e5f6
Create Date: 2026-01-16 10:00:00.000000

This migration:
1. Creates the junction table 'atividade_projeto' for N:N relationship
2. Migrates existing data from atividades.id_projeto to the new table
3. Removes the id_projeto column from atividades table
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

# revision identifiers, used by Alembic.
revision: str = 'b2c3d4e5f6g7'
down_revision: Union[str, None] = 'a1b2c3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Create the junction table atividade_projeto
    op.create_table(
        'atividade_projeto',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('id_atividade', UUID(as_uuid=True), nullable=False),
        sa.Column('id_projeto', UUID(as_uuid=True), nullable=False),
        sa.Column('criado_em', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['id_atividade'], ['api_aponta.atividades.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['id_projeto'], ['api_aponta.projetos.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('id_atividade', 'id_projeto', name='uq_atividade_projeto'),
        schema='api_aponta'
    )

    # Create indexes for better query performance
    op.create_index(
        'ix_api_aponta_atividade_projeto_id_atividade',
        'atividade_projeto',
        ['id_atividade'],
        schema='api_aponta'
    )
    op.create_index(
        'ix_api_aponta_atividade_projeto_id_projeto',
        'atividade_projeto',
        ['id_projeto'],
        schema='api_aponta'
    )

    # 2. Migrate existing data from atividades.id_projeto to the junction table
    op.execute("""
        INSERT INTO api_aponta.atividade_projeto (id_atividade, id_projeto)
        SELECT id, id_projeto
        FROM api_aponta.atividades
        WHERE id_projeto IS NOT NULL
    """)

    # 3. Drop the index on id_projeto column
    op.drop_index(
        'ix_api_aponta_atividades_id_projeto',
        table_name='atividades',
        schema='api_aponta'
    )

    # 4. Drop the id_projeto column from atividades
    op.drop_column('atividades', 'id_projeto', schema='api_aponta')


def downgrade() -> None:
    # 1. Add back the id_projeto column
    op.add_column(
        'atividades',
        sa.Column(
            'id_projeto',
            UUID(as_uuid=True),
            nullable=True,
            comment='Project ID from Azure Boards (Azure DevOps)'
        ),
        schema='api_aponta'
    )

    # 2. Restore data from junction table (takes first project if multiple)
    op.execute("""
        UPDATE api_aponta.atividades a
        SET id_projeto = (
            SELECT ap.id_projeto
            FROM api_aponta.atividade_projeto ap
            WHERE ap.id_atividade = a.id
            LIMIT 1
        )
    """)

    # 3. Make id_projeto NOT NULL after data restoration
    op.alter_column(
        'atividades',
        'id_projeto',
        nullable=False,
        schema='api_aponta'
    )

    # 4. Recreate the index on id_projeto
    op.create_index(
        'ix_api_aponta_atividades_id_projeto',
        'atividades',
        ['id_projeto'],
        schema='api_aponta'
    )

    # 5. Drop indexes from junction table
    op.drop_index(
        'ix_api_aponta_atividade_projeto_id_projeto',
        table_name='atividade_projeto',
        schema='api_aponta'
    )
    op.drop_index(
        'ix_api_aponta_atividade_projeto_id_atividade',
        table_name='atividade_projeto',
        schema='api_aponta'
    )

    # 6. Drop the junction table
    op.drop_table('atividade_projeto', schema='api_aponta')
