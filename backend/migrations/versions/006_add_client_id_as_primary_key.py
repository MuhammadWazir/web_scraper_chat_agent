"""add client_id as primary key

Revision ID: 006
Revises: 005
Create Date: 2026-02-16 14:20:00.000000

"""
from typing import Sequence, Union
import uuid

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '006'
down_revision: Union[str, None] = '005'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    connection = op.get_bind()
    
    # Step 1: Drop foreign keys that reference client_ip (if they exist)
    # Check and drop chats foreign key
    result = connection.execute(sa.text("""
        SELECT constraint_name 
        FROM information_schema.table_constraints 
        WHERE table_name = 'chats' 
        AND constraint_type = 'FOREIGN KEY'
        AND constraint_name = 'chats_client_ip_fkey'
    """))
    if result.fetchone():
        op.drop_constraint('chats_client_ip_fkey', 'chats', type_='foreignkey')
    
    # Check and drop widget_sessions foreign key
    result = connection.execute(sa.text("""
        SELECT constraint_name 
        FROM information_schema.table_constraints 
        WHERE table_name = 'widget_sessions' 
        AND constraint_type = 'FOREIGN KEY'
        AND constraint_name = 'widget_sessions_client_ip_fkey'
    """))
    if result.fetchone():
        op.drop_constraint('widget_sessions_client_ip_fkey', 'widget_sessions', type_='foreignkey')
    
    # Step 2: Drop the primary key constraint on client_ip in clients table (if it exists)
    result = connection.execute(sa.text("""
        SELECT constraint_name 
        FROM information_schema.table_constraints 
        WHERE table_name = 'clients' 
        AND constraint_type = 'PRIMARY KEY'
    """))
    if result.fetchone():
        op.drop_constraint('clients_pkey', 'clients', type_='primary')
    
    # Step 3: Add client_id column to clients table with UUID values (if it doesn't exist)
    result = connection.execute(sa.text("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = 'clients' 
        AND column_name = 'client_id'
    """))
    if not result.fetchone():
        op.add_column('clients', sa.Column('client_id', sa.String(), nullable=True))
    
    # Step 4: Populate client_id with UUIDs for existing rows
    connection.execute(sa.text("""
        UPDATE clients 
        SET client_id = gen_random_uuid()::text
        WHERE client_id IS NULL
    """))
    
    # Step 5: Make client_id NOT NULL and set as primary key
    op.alter_column('clients', 'client_id', nullable=False)
    op.create_primary_key('clients_pkey', 'clients', ['client_id'])
    
    # Step 6: Make client_ip a regular indexed column (no longer primary key)
    op.alter_column('clients', 'client_ip', nullable=False)
    
    # Step 7: Add client_id columns to chats and widget_sessions tables (if they don't exist)
    result = connection.execute(sa.text("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = 'chats' 
        AND column_name = 'client_id'
    """))
    if not result.fetchone():
        op.add_column('chats', sa.Column('client_id', sa.String(), nullable=True))
    
    result = connection.execute(sa.text("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = 'widget_sessions' 
        AND column_name = 'client_id'
    """))
    if not result.fetchone():
        op.add_column('widget_sessions', sa.Column('client_id', sa.String(), nullable=True))
    
    # Step 8: Populate client_id in chats and widget_sessions from the mapping
    connection.execute(sa.text("""
        UPDATE chats 
        SET client_id = clients.client_id
        FROM clients
        WHERE chats.client_ip = clients.client_ip
    """))
    
    connection.execute(sa.text("""
        UPDATE widget_sessions 
        SET client_id = clients.client_id
        FROM clients
        WHERE widget_sessions.client_ip = clients.client_ip
    """))
    
    # Step 9: Make client_id NOT NULL in chats and widget_sessions
    op.alter_column('chats', 'client_id', nullable=False)
    op.alter_column('widget_sessions', 'client_id', nullable=False)
    
    # Step 10: Drop old client_ip columns from chats and widget_sessions (if they exist)
    result = connection.execute(sa.text("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = 'chats' 
        AND column_name = 'client_ip'
    """))
    if result.fetchone():
        op.drop_column('chats', 'client_ip')
    
    result = connection.execute(sa.text("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = 'widget_sessions' 
        AND column_name = 'client_ip'
    """))
    if result.fetchone():
        op.drop_column('widget_sessions', 'client_ip')
    
    # Step 11: Create foreign keys with new client_id columns
    op.create_foreign_key('chats_client_id_fkey', 'chats', 'clients', ['client_id'], ['client_id'], ondelete='CASCADE')
    op.create_foreign_key('widget_sessions_client_id_fkey', 'widget_sessions', 'clients', ['client_id'], ['client_id'], ondelete='CASCADE')


def downgrade() -> None:
    # Reverse the changes
    op.drop_constraint('widget_sessions_client_id_fkey', 'widget_sessions', type_='foreignkey')
    op.drop_constraint('chats_client_id_fkey', 'chats', type_='foreignkey')
    
    # Add back client_ip columns to chats and widget_sessions
    op.add_column('chats', sa.Column('client_ip', sa.String(), nullable=True))
    op.add_column('widget_sessions', sa.Column('client_ip', sa.String(), nullable=True))
    
    # Populate client_ip from the mapping
    connection = op.get_bind()
    connection.execute(sa.text("""
        UPDATE chats 
        SET client_ip = clients.client_ip
        FROM clients
        WHERE chats.client_id = clients.client_id
    """))
    
    connection.execute(sa.text("""
        UPDATE widget_sessions 
        SET client_ip = clients.client_ip
        FROM clients
        WHERE widget_sessions.client_id = clients.client_id
    """))
    
    # Make client_ip NOT NULL
    op.alter_column('chats', 'client_ip', nullable=False)
    op.alter_column('widget_sessions', 'client_ip', nullable=False)
    
    # Drop client_id columns
    op.drop_column('chats', 'client_id')
    op.drop_column('widget_sessions', 'client_id')
    
    # Recreate foreign keys with client_ip
    op.create_foreign_key('widget_sessions_client_ip_fkey', 'widget_sessions', 'clients', ['client_ip'], ['client_ip'], ondelete='CASCADE')
    op.create_foreign_key('chats_client_ip_fkey', 'chats', 'clients', ['client_ip'], ['client_ip'], ondelete='CASCADE')
    
    # Drop client_id from clients table
    op.drop_constraint('clients_pkey', 'clients', type_='primary')
    op.drop_column('clients', 'client_id')
    
    # Recreate primary key on client_ip
    op.create_primary_key('clients_pkey', 'clients', ['client_ip'])
