"""add_tools_to_clients

Revision ID: 004
Revises: 003
Create Date: 2026-01-27 18:54:40.256968

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '004'
down_revision: Union[str, None] = '003'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('clients', sa.Column('tools', sa.JSON(), nullable=True))


def downgrade() -> None:
    op.drop_column('clients', 'tools')
