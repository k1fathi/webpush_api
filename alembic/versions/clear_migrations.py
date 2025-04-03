"""Reset migrations due to type incompatibility

Revision ID: clear_migrations
Revises: 
Create Date: 2025-04-03 20:00:00

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'clear_migrations'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    """
    This is a fresh start migration after fixing data type inconsistencies.
    Previous migrations had incompatible data types for foreign keys.
    """
    # Drop existing tables if they exist to avoid conflicts
    op.execute("DROP TABLE IF EXISTS cep_decisions CASCADE")
    op.execute("DROP TABLE IF EXISTS campaigns CASCADE")
    op.execute("DROP TABLE IF EXISTS users CASCADE")
    
    # PostgreSQL type definitions - create them if they don't exist
    op.execute("DO $$ BEGIN IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'campaign_status_enum') THEN CREATE TYPE campaign_status_enum AS ENUM ('draft', 'scheduled', 'running', 'paused', 'completed', 'cancelled'); END IF; END $$;")
    op.execute("DO $$ BEGIN IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'campaign_type_enum') THEN CREATE TYPE campaign_type_enum AS ENUM ('one_time', 'recurring', 'trigger_based', 'ab_test'); END IF; END $$;")
    op.execute("DO $$ BEGIN IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'user_status_enum') THEN CREATE TYPE user_status_enum AS ENUM ('active', 'inactive', 'pending', 'blocked', 'deleted'); END IF; END $$;")
    
    # Create tables with consistent UUID types
    
    # Users table
    op.create_table('users',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('email', sa.String(), nullable=False, unique=True),
        sa.Column('username', sa.String(), nullable=True, unique=True),
        sa.Column('hashed_password', sa.String(), nullable=False),
        sa.Column('full_name', sa.String(), nullable=True),
        sa.Column('status', sa.Enum('active', 'inactive', 'pending', 'blocked', 'deleted', name='user_status_enum'), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()'))
    )
    
    # Campaigns table
    op.create_table('campaigns',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('scheduled_time', sa.DateTime(), nullable=True),
        sa.Column('status', sa.Enum('draft', 'scheduled', 'running', 'paused', 'completed', 'cancelled', name='campaign_status_enum'), nullable=False),
        sa.Column('is_recurring', sa.Boolean(), nullable=False, default=False),
        sa.Column('recurrence_pattern', sa.String(), nullable=True),
        sa.Column('campaign_type', sa.Enum('one_time', 'recurring', 'trigger_based', 'ab_test', name='campaign_type_enum'), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()'))
    )
    
    # CEP Decisions table
    op.create_table('cep_decisions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('campaign_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('campaigns.id'), nullable=False),
        sa.Column('decision_time', sa.DateTime(), nullable=True),
        sa.Column('selected_channel', sa.String(50), nullable=False),
        sa.Column('score', sa.Float(), nullable=False, default=0.0),
        sa.Column('factors', postgresql.JSON(astext_type=sa.Text()), nullable=False, server_default='{}'),
        sa.Column('alternative_channels', postgresql.JSON(astext_type=sa.Text()), nullable=False, server_default='[]'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()'))
    )

def downgrade():
    # Drop tables in reverse order (respecting foreign keys)
    op.drop_table('cep_decisions')
    op.drop_table('campaigns')
    op.drop_table('users')
    
    # Drop types
    op.execute("DROP TYPE IF EXISTS campaign_status_enum")
    op.execute("DROP TYPE IF EXISTS campaign_type_enum")
    op.execute("DROP TYPE IF EXISTS user_status_enum")
