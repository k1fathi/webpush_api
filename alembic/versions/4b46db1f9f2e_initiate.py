"""initiate

Revision ID: 4b46db1f9f2e
Revises: 
Create Date: 2025-04-10 14:36:41.031001

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '4b46db1f9f2e'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('permissions',
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('description', sa.String(), nullable=True),
    sa.Column('category', sa.String(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('name')
    )
    op.create_table('roles',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('description', sa.String(), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_roles_name'), 'roles', ['name'], unique=True)
    op.create_table('segments',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('segment_type', postgresql.ENUM('DYNAMIC', 'STATIC', name='segment_type_enum'), nullable=True),
    sa.Column('filter_criteria', sa.JSON(), nullable=True),
    sa.Column('user_count', sa.Integer(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.Column('last_evaluated_at', sa.DateTime(), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('triggers',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('trigger_type', postgresql.ENUM('EVENT', 'SCHEDULE', 'BEHAVIOR', 'COMPOSITE', name='trigger_type_enum'), nullable=False),
    sa.Column('status', postgresql.ENUM('ACTIVE', 'INACTIVE', 'PAUSED', 'ERROR', name='trigger_status_enum'), nullable=True),
    sa.Column('rules', sa.JSON(), nullable=False),
    sa.Column('schedule', sa.JSON(), nullable=True),
    sa.Column('action', sa.JSON(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.Column('last_triggered_at', sa.DateTime(), nullable=True),
    sa.Column('trigger_count', sa.Integer(), nullable=True),
    sa.Column('error_count', sa.Integer(), nullable=True),
    sa.Column('trigger_metadata', sa.JSON(), nullable=True),
    sa.Column('cooldown_period', sa.Interval(), nullable=True),
    sa.Column('max_triggers_per_day', sa.Integer(), nullable=True),
    sa.Column('enabled', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('role_permission',
    sa.Column('role_id', sa.UUID(), nullable=False),
    sa.Column('permission_name', sa.String(), nullable=False),
    sa.ForeignKeyConstraint(['permission_name'], ['permissions.name'], ),
    sa.ForeignKeyConstraint(['role_id'], ['roles.id'], ),
    sa.PrimaryKeyConstraint('role_id', 'permission_name')
    )
    op.create_table('role_permissions',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('role_id', sa.UUID(), nullable=False),
    sa.Column('permission_name', sa.String(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['role_id'], ['roles.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('trigger_executions',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('trigger_id', sa.UUID(), nullable=False),
    sa.Column('executed_at', sa.DateTime(), nullable=True),
    sa.Column('success', sa.Boolean(), nullable=False),
    sa.Column('action_result', sa.JSON(), nullable=True),
    sa.Column('error', sa.Text(), nullable=True),
    sa.ForeignKeyConstraint(['trigger_id'], ['triggers.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('users',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('email', sa.String(), nullable=False),
    sa.Column('username', sa.String(), nullable=True),
    sa.Column('hashed_password', sa.String(), nullable=False),
    sa.Column('full_name', sa.String(), nullable=True),
    sa.Column('status', postgresql.ENUM('ACTIVE', 'INACTIVE', 'PENDING', 'BLOCKED', 'DELETED', name='user_status_enum'), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=True),
    sa.Column('is_superuser', sa.Boolean(), nullable=True),
    sa.Column('notification_enabled', sa.Boolean(), nullable=True),
    sa.Column('webpush_enabled', sa.Boolean(), nullable=True),
    sa.Column('email_notification_enabled', sa.Boolean(), nullable=True),
    sa.Column('quiet_hours_start', sa.Integer(), nullable=True),
    sa.Column('quiet_hours_end', sa.Integer(), nullable=True),
    sa.Column('subscription_info', sa.JSON(), nullable=True),
    sa.Column('devices', sa.JSON(), nullable=True),
    sa.Column('timezone', sa.String(), nullable=True),
    sa.Column('language', sa.String(), nullable=True),
    sa.Column('custom_attributes', sa.JSON(), nullable=True),
    sa.Column('role_id', sa.UUID(), nullable=True),
    sa.Column('permissions', postgresql.ARRAY(sa.String()), nullable=True),
    sa.Column('last_login', sa.DateTime(), nullable=True),
    sa.Column('last_seen', sa.DateTime(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['role_id'], ['roles.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=True)
    op.create_table('campaign_templates',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('description', sa.String(), nullable=True),
    sa.Column('category', sa.Enum('PROMOTIONAL', 'TRANSACTIONAL', 'INFORMATIONAL', 'REMINDER', 'SURVEY', name='templatecategory'), nullable=True),
    sa.Column('status', sa.Enum('DRAFT', 'ACTIVE', 'ARCHIVED', 'DEPRECATED', name='templatestatus'), nullable=True),
    sa.Column('content', sa.JSON(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.Column('created_by', sa.UUID(), nullable=True),
    sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_campaign_templates_id'), 'campaign_templates', ['id'], unique=False)
    op.create_index(op.f('ix_campaign_templates_name'), 'campaign_templates', ['name'], unique=False)
    op.create_table('cdp_integrations',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('user_id', sa.UUID(), nullable=False),
    sa.Column('user_profile_data', sa.JSON(), nullable=True),
    sa.Column('behavioral_data', sa.JSON(), nullable=True),
    sa.Column('last_synced', sa.DateTime(), nullable=True),
    sa.Column('sync_status', sa.Enum('PENDING', 'IN_PROGRESS', 'SUCCESS', 'ERROR', 'SKIPPED', name='cdp_sync_status'), nullable=True),
    sa.Column('error_message', sa.String(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('templates',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('title', sa.String(), nullable=False),
    sa.Column('body', sa.Text(), nullable=False),
    sa.Column('image_url', sa.String(), nullable=True),
    sa.Column('action_url', sa.String(), nullable=True),
    sa.Column('icon_url', sa.String(), nullable=True),
    sa.Column('template_type', postgresql.ENUM('WEBPUSH', 'EMAIL', 'SMS', 'IN_APP', 'MOBILE_PUSH', name='template_type_enum'), nullable=True),
    sa.Column('content', sa.JSON(), nullable=True),
    sa.Column('variables', postgresql.ARRAY(sa.String()), nullable=True),
    sa.Column('tags', postgresql.ARRAY(sa.String()), nullable=True),
    sa.Column('category', sa.String(), nullable=True),
    sa.Column('status', postgresql.ENUM('DRAFT', 'ACTIVE', 'ARCHIVED', 'DELETED', name='template_status_enum'), nullable=True),
    sa.Column('version', sa.Integer(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.Column('created_by', sa.UUID(), nullable=True),
    sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('user_role',
    sa.Column('user_id', sa.UUID(), nullable=False),
    sa.Column('role_id', sa.UUID(), nullable=False),
    sa.ForeignKeyConstraint(['role_id'], ['roles.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('user_id', 'role_id')
    )
    op.create_table('user_roles',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('user_id', sa.UUID(), nullable=False),
    sa.Column('role_id', sa.UUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['role_id'], ['roles.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('user_segment',
    sa.Column('user_id', sa.UUID(), nullable=False),
    sa.Column('segment_id', sa.UUID(), nullable=False),
    sa.ForeignKeyConstraint(['segment_id'], ['segments.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('user_id', 'segment_id')
    )
    op.create_table('campaigns',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('scheduled_time', sa.DateTime(), nullable=True),
    sa.Column('status', postgresql.ENUM('DRAFT', 'SCHEDULED', 'RUNNING', 'COMPLETED', 'PAUSED', 'CANCELLED', name='campaign_status_enum'), nullable=True),
    sa.Column('is_recurring', sa.Boolean(), nullable=True),
    sa.Column('recurrence_pattern', sa.String(), nullable=True),
    sa.Column('campaign_type', postgresql.ENUM('ONE_TIME', 'RECURRING', 'TRIGGERED', name='campaign_type_enum'), nullable=True),
    sa.Column('segment_id', sa.UUID(), nullable=True),
    sa.Column('template_id', sa.UUID(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['segment_id'], ['segments.id'], ),
    sa.ForeignKeyConstraint(['template_id'], ['templates.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('template_versions',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('template_id', sa.UUID(), nullable=False),
    sa.Column('version', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(), nullable=False),
    sa.Column('body', sa.Text(), nullable=False),
    sa.Column('image_url', sa.String(), nullable=True),
    sa.Column('action_url', sa.String(), nullable=True),
    sa.Column('icon_url', sa.String(), nullable=True),
    sa.Column('content', sa.JSON(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('created_by', sa.UUID(), nullable=True),
    sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
    sa.ForeignKeyConstraint(['template_id'], ['templates.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('ab_tests',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('campaign_id', sa.UUID(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('variant_count', sa.Integer(), nullable=True),
    sa.Column('winning_criteria', postgresql.ENUM('OPEN_RATE', 'CLICK_RATE', 'CONVERSION', 'ENGAGEMENT', name='winning_criteria_enum'), nullable=True),
    sa.Column('start_date', sa.DateTime(), nullable=True),
    sa.Column('end_date', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['campaign_id'], ['campaigns.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('cep_decisions',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('user_id', sa.UUID(), nullable=False),
    sa.Column('campaign_id', sa.UUID(), nullable=False),
    sa.Column('decision_time', sa.DateTime(), nullable=True),
    sa.Column('selected_channel', sa.String(length=50), nullable=False),
    sa.Column('score', sa.Float(), nullable=False),
    sa.Column('factors', sa.JSON(), nullable=False),
    sa.Column('alternative_channels', sa.JSON(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['campaign_id'], ['campaigns.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('test_variants',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('ab_test_id', sa.UUID(), nullable=False),
    sa.Column('template_id', sa.UUID(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('sent_count', sa.Integer(), nullable=True),
    sa.Column('opened_count', sa.Integer(), nullable=True),
    sa.Column('clicked_count', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['ab_test_id'], ['ab_tests.id'], ),
    sa.ForeignKeyConstraint(['template_id'], ['templates.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('notifications',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('campaign_id', sa.UUID(), nullable=True),
    sa.Column('user_id', sa.UUID(), nullable=False),
    sa.Column('template_id', sa.UUID(), nullable=True),
    sa.Column('title', sa.String(), nullable=False),
    sa.Column('body', sa.String(), nullable=False),
    sa.Column('image_url', sa.String(), nullable=True),
    sa.Column('action_url', sa.String(), nullable=True),
    sa.Column('variant_id', sa.UUID(), nullable=True),
    sa.Column('personalized_data', sa.JSON(), nullable=True),
    sa.Column('delivery_status', postgresql.ENUM('PENDING', 'QUEUED', 'SENDING', 'DELIVERED', 'FAILED', 'OPENED', 'CLICKED', name='delivery_status_enum'), nullable=True),
    sa.Column('notification_type', postgresql.ENUM('CAMPAIGN', 'TRIGGERED', 'TRANSACTIONAL', 'AUTOMATED', 'TEST', name='notification_type_enum'), nullable=True),
    sa.Column('sent_at', sa.DateTime(), nullable=True),
    sa.Column('delivered_at', sa.DateTime(), nullable=True),
    sa.Column('opened_at', sa.DateTime(), nullable=True),
    sa.Column('clicked_at', sa.DateTime(), nullable=True),
    sa.Column('device_info', sa.JSON(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['campaign_id'], ['campaigns.id'], ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.ForeignKeyConstraint(['variant_id'], ['test_variants.id'], ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_notifications_campaign_id'), 'notifications', ['campaign_id'], unique=False)
    op.create_index(op.f('ix_notifications_user_id'), 'notifications', ['user_id'], unique=False)
    op.create_table('analytics',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('notification_id', sa.UUID(), nullable=False),
    sa.Column('campaign_id', sa.UUID(), nullable=False),
    sa.Column('user_id', sa.UUID(), nullable=False),
    sa.Column('delivered', sa.Boolean(), nullable=True),
    sa.Column('opened', sa.Boolean(), nullable=True),
    sa.Column('clicked', sa.Boolean(), nullable=True),
    sa.Column('event_time', sa.DateTime(), nullable=True),
    sa.Column('user_action', sa.String(), nullable=True),
    sa.Column('conversion_type', postgresql.ENUM('PURCHASE', 'SIGNUP', 'PAGEVIEW', 'DOWNLOAD', 'CUSTOM', name='conversion_type_enum'), nullable=True),
    sa.Column('conversion_value', sa.Float(), nullable=True),
    sa.ForeignKeyConstraint(['campaign_id'], ['campaigns.id'], ),
    sa.ForeignKeyConstraint(['notification_id'], ['notifications.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('analytics')
    op.drop_index(op.f('ix_notifications_user_id'), table_name='notifications')
    op.drop_index(op.f('ix_notifications_campaign_id'), table_name='notifications')
    op.drop_table('notifications')
    op.drop_table('test_variants')
    op.drop_table('cep_decisions')
    op.drop_table('ab_tests')
    op.drop_table('template_versions')
    op.drop_table('campaigns')
    op.drop_table('user_segment')
    op.drop_table('user_roles')
    op.drop_table('user_role')
    op.drop_table('templates')
    op.drop_table('cdp_integrations')
    op.drop_index(op.f('ix_campaign_templates_name'), table_name='campaign_templates')
    op.drop_index(op.f('ix_campaign_templates_id'), table_name='campaign_templates')
    op.drop_table('campaign_templates')
    op.drop_index(op.f('ix_users_username'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')
    op.drop_table('trigger_executions')
    op.drop_table('role_permissions')
    op.drop_table('role_permission')
    op.drop_table('triggers')
    op.drop_table('segments')
    op.drop_index(op.f('ix_roles_name'), table_name='roles')
    op.drop_table('roles')
    op.drop_table('permissions')
    # ### end Alembic commands ###
