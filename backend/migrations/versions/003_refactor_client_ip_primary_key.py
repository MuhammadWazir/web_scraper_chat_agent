"""refactor client id to client ip

Revision ID: 003
Revises: 002
Create Date: 2026-01-23 19:20:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '003'
down_revision: Union[str, None] = '002'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Step 1: Drop foreign keys that reference client_id
    op.drop_constraint('chats_client_id_fkey', 'chats', type_='foreignkey')
    op.drop_constraint('widget_sessions_client_id_fkey', 'widget_sessions', type_='foreignkey')
    
    # Step 2: Rename client_id to client_ip in clients table
    op.alter_column('clients', 'client_id', new_column_name='client_ip')
    
    # Step 3: Rename client_id to client_ip in chats table (FK column)
    op.alter_column('chats', 'client_id', new_column_name='client_ip')
    
    # Step 4: Rename client_id to client_ip in widget_sessions table (FK column)
    op.alter_column('widget_sessions', 'client_id', new_column_name='client_ip')
    
    # Step 5: Recreate foreign keys with new column names
    op.create_foreign_key('chats_client_ip_fkey', 'chats', 'clients', ['client_ip'], ['client_ip'], ondelete='CASCADE')
    op.create_foreign_key('widget_sessions_client_ip_fkey', 'widget_sessions', 'clients', ['client_ip'], ['client_ip'], ondelete='CASCADE')


def downgrade() -> None:
    # Reverse the changes
    op.drop_constraint('widget_sessions_client_ip_fkey', 'widget_sessions', type_='foreignkey')
    op.drop_constraint('chats_client_ip_fkey', 'chats', type_='foreignkey')
    
    # Rename back
    op.alter_column('widget_sessions', 'client_ip', new_column_name='client_id')
    op.alter_column('chats', 'client_ip', new_column_name='client_id')
    op.alter_column('clients', 'client_ip', new_column_name='client_id')
    
    # Recreate original foreign keys
    op.create_foreign_key('widget_sessions_client_id_fkey', 'widget_sessions', 'clients', ['client_id'], ['client_id'], ondelete='CASCADE')
    op.create_foreign_key('chats_client_id_fkey', 'chats', 'clients', ['client_id'], ['client_id'], ondelete='CASCADE')
