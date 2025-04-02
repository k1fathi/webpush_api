"""add user subscription fields

Revision ID: xxx
Revises: previous_revision_id
Create Date: 2023-06-15 10:00:00

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic
revision = 'xxx'  # replace with a unique identifier
down_revision = 'previous_revision_id'  # replace with the previous revision ID
branch_labels = None
depends_on = None

def upgrade():
    # Add notification preferences fields to users table
    op.add_column('users', sa.Column('notification_enabled', sa.Boolean(), nullable=False, server_default='true'))
    op.add_column('users', sa.Column('webpush_enabled', sa.Boolean(), nullable=False, server_default='true'))
    op.add_column('users', sa.Column('email_notification_enabled', sa.Boolean(), nullable=False, server_default='true'))
    op.add_column('users', sa.Column('quiet_hours_start', sa.Integer(), nullable=True))
    op.add_column('users', sa.Column('quiet_hours_end', sa.Integer(), nullable=True))
    
    # Add subscription info and devices columns
    op.add_column('users', sa.Column('subscription_info', postgresql.JSONB(astext_type=sa.Text()), nullable=True))
    op.add_column('users', sa.Column('devices', postgresql.JSONB(astext_type=sa.Text()), nullable=True))
    
    # Add user attributes fields
    op.add_column('users', sa.Column('timezone', sa.String(), nullable=True, server_default='UTC'))
    op.add_column('users', sa.Column('language', sa.String(), nullable=True, server_default='en'))
    op.add_column('users', sa.Column('custom_attributes', postgresql.JSONB(astext_type=sa.Text()), nullable=True))
    
    # Add tracking fields
    op.add_column('users', sa.Column('last_login', sa.DateTime(), nullable=True))
    op.add_column('users', sa.Column('last_seen', sa.DateTime(), nullable=True))

def downgrade():
    # Remove all added columns
    op.drop_column('users', 'last_seen')
    op.drop_column('users', 'last_login')
    op.drop_column('users', 'custom_attributes')
    op.drop_column('users', 'language')
    op.drop_column('users', 'timezone')
    op.drop_column('users', 'devices')
    op.drop_column('users', 'subscription_info')
    op.drop_column('users', 'quiet_hours_end')
    op.drop_column('users', 'quiet_hours_start')
    op.drop_column('users', 'email_notification_enabled')
    op.drop_column('users', 'webpush_enabled')
    op.drop_column('users', 'notification_enabled')
