"""dummy_migration

Revision ID: ebd442876620
Revises: 
Create Date: 2026-01-01 16:19:12.941939

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ebd442876620'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Esta migração é agora um dummy para permitir que o 
    # ambiente remoto (OpenShift) que já registrou essa versão 
    # consiga encontrar o arquivo e prosseguir para a próxima.
    pass


def downgrade() -> None:
    pass
