"""add_system_prompt_to_clients

Revision ID: 005
Revises: 004
Create Date: 2026-01-29 21:40:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '005'
down_revision: Union[str, None] = '004'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('clients', sa.Column('system_prompt', sa.Text(), nullable=True, server_default=''))


def downgrade() -> None:
    op.drop_column('clients', 'system_prompt')
