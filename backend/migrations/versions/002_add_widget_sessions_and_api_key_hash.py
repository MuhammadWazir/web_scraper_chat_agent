"""add widget sessions and api key hash

Revision ID: 002
Revises: 001
Create Date: 2026-01-23 18:20:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '002'
down_revision: Union[str, None] = '001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add api_key_hash column to clients table
    op.add_column('clients', sa.Column('api_key_hash', sa.String(255), nullable=True))
    op.create_index(op.f('ix_clients_api_key_hash'), 'clients', ['api_key_hash'], unique=True)
    
    # Create widget_sessions table
    op.create_table(
        'widget_sessions',
        sa.Column('session_token', sa.String(), nullable=False),
        sa.Column('client_id', sa.String(), nullable=False),
        sa.Column('end_user_ip', sa.String(45), nullable=True),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.ForeignKeyConstraint(['client_id'], ['clients.client_id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('session_token')
    )
    
    # Create indexes
    op.create_index(op.f('ix_widget_sessions_session_token'), 'widget_sessions', ['session_token'], unique=False)
    op.create_index(op.f('ix_widget_sessions_client_id'), 'widget_sessions', ['client_id'], unique=False)


def downgrade() -> None:
    # Drop widget_sessions table and indexes
    op.drop_index(op.f('ix_widget_sessions_client_id'), table_name='widget_sessions')
    op.drop_index(op.f('ix_widget_sessions_session_token'), table_name='widget_sessions')
    op.drop_table('widget_sessions')
    
    # Remove api_key_hash from clients table
    op.drop_index(op.f('ix_clients_api_key_hash'), table_name='clients')
    op.drop_column('clients', 'api_key_hash')
