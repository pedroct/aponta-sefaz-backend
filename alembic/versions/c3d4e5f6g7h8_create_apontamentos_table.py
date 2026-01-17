"""Create apontamentos table

Revision ID: c3d4e5f6g7h8
Revises: b2c3d4e5f6g7
Create Date: 2026-01-17 10:00:00.000000

This migration creates the apontamentos table for tracking work hours.
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

# revision identifiers, used by Alembic.
revision: str = 'c3d4e5f6g7h8'
down_revision: Union[str, None] = 'b2c3d4e5f6g7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create the apontamentos table
    op.create_table(
        'apontamentos',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('work_item_id', sa.Integer(), nullable=False, comment='ID do Work Item no Azure DevOps'),
        sa.Column('project_id', sa.String(255), nullable=False, comment='ID do projeto no Azure DevOps'),
        sa.Column('organization_name', sa.String(255), nullable=False, comment='Nome da organização no Azure DevOps'),
        sa.Column('data_apontamento', sa.Date(), nullable=False, comment='Data em que o trabalho foi realizado'),
        sa.Column('horas', sa.Integer(), nullable=False, comment='Quantidade de horas trabalhadas (0-8)'),
        sa.Column('minutos', sa.Integer(), nullable=False, comment='Quantidade de minutos trabalhados (0, 15, 30, 45)'),
        sa.Column('id_atividade', UUID(as_uuid=True), nullable=False, comment='ID da atividade associada'),
        sa.Column('comentario', sa.String(100), nullable=True, comment='Comentário sobre o trabalho realizado'),
        sa.Column('usuario_id', sa.String(255), nullable=False, comment='ID do usuário no Azure DevOps'),
        sa.Column('usuario_nome', sa.String(255), nullable=False, comment='Nome de exibição do usuário'),
        sa.Column('usuario_email', sa.String(255), nullable=True, comment='Nome de login do usuário'),
        sa.Column('criado_em', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column('atualizado_em', sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['id_atividade'], ['api_aponta.atividades.id'], ondelete='RESTRICT'),
        schema='api_aponta'
    )

    # Create indexes for better query performance
    op.create_index(
        'ix_api_aponta_apontamentos_id',
        'apontamentos',
        ['id'],
        schema='api_aponta'
    )
    op.create_index(
        'ix_api_aponta_apontamentos_work_item_id',
        'apontamentos',
        ['work_item_id'],
        schema='api_aponta'
    )
    op.create_index(
        'ix_api_aponta_apontamentos_project_id',
        'apontamentos',
        ['project_id'],
        schema='api_aponta'
    )
    op.create_index(
        'ix_api_aponta_apontamentos_organization_name',
        'apontamentos',
        ['organization_name'],
        schema='api_aponta'
    )
    op.create_index(
        'ix_api_aponta_apontamentos_data_apontamento',
        'apontamentos',
        ['data_apontamento'],
        schema='api_aponta'
    )
    op.create_index(
        'ix_api_aponta_apontamentos_id_atividade',
        'apontamentos',
        ['id_atividade'],
        schema='api_aponta'
    )
    op.create_index(
        'ix_api_aponta_apontamentos_usuario_id',
        'apontamentos',
        ['usuario_id'],
        schema='api_aponta'
    )
    # Composite index for common queries (work item + organization + project)
    op.create_index(
        'ix_api_aponta_apontamentos_work_item_org_project',
        'apontamentos',
        ['work_item_id', 'organization_name', 'project_id'],
        schema='api_aponta'
    )


def downgrade() -> None:
    # Drop indexes
    op.drop_index('ix_api_aponta_apontamentos_work_item_org_project', table_name='apontamentos', schema='api_aponta')
    op.drop_index('ix_api_aponta_apontamentos_usuario_id', table_name='apontamentos', schema='api_aponta')
    op.drop_index('ix_api_aponta_apontamentos_id_atividade', table_name='apontamentos', schema='api_aponta')
    op.drop_index('ix_api_aponta_apontamentos_data_apontamento', table_name='apontamentos', schema='api_aponta')
    op.drop_index('ix_api_aponta_apontamentos_organization_name', table_name='apontamentos', schema='api_aponta')
    op.drop_index('ix_api_aponta_apontamentos_project_id', table_name='apontamentos', schema='api_aponta')
    op.drop_index('ix_api_aponta_apontamentos_work_item_id', table_name='apontamentos', schema='api_aponta')
    op.drop_index('ix_api_aponta_apontamentos_id', table_name='apontamentos', schema='api_aponta')

    # Drop table
    op.drop_table('apontamentos', schema='api_aponta')
