"""Initial migration

Revision ID: c7fd83cf7ae8
Revises: 
Create Date: 2023-04-02 20:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'c7fd83cf7ae8'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Create enum types first
    op.execute("CREATE TYPE user_status_enum AS ENUM ('active', 'inactive', 'pending', 'blocked', 'deleted');")
    op.execute("CREATE TYPE campaign_status_enum AS ENUM ('draft', 'scheduled', 'running', 'paused', 'completed', 'cancelled');")
    op.execute("CREATE TYPE campaign_type_enum AS ENUM ('one_time', 'recurring', 'trigger_based', 'ab_test');")
    op.execute("CREATE TYPE trigger_type_enum AS ENUM ('event', 'schedule', 'behavior', 'composite');")
    op.execute("CREATE TYPE trigger_status_enum AS ENUM ('active', 'inactive', 'paused', 'error');")
    op.execute("CREATE TYPE delivery_status_enum AS ENUM ('pending', 'queued', 'sending', 'delivered', 'failed', 'opened', 'clicked');")
    op.execute("CREATE TYPE template_type_enum AS ENUM ('webpush', 'email', 'sms', 'in_app', 'mobile_push');")
    op.execute("CREATE TYPE template_status_enum AS ENUM ('draft', 'active', 'archived', 'deleted');")
    op.execute("CREATE TYPE segment_type_enum AS ENUM ('static', 'dynamic', 'behavioral', 'composite');")
    op.execute("CREATE TYPE winning_criteria_enum AS ENUM ('open_rate', 'click_rate', 'conversion', 'engagement');")
    op.execute("CREATE TYPE conversion_type_enum AS ENUM ('purchase', 'signup', 'pageview', 'download', 'custom');")
    
    # Create tables
    op.create_table('permissions',
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('name')
    )
    
    op.create_table('roles',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_roles_name'), 'roles', ['name'], unique=True)
    
    op.create_table('segments',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('segment_type', sa.Enum('static', 'dynamic', 'behavioral', 'composite', name='segment_type_enum'), nullable=True),
        sa.Column('filter_criteria', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('user_count', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('last_evaluated_at', sa.DateTime(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    op.create_table('users',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('username', sa.String(), nullable=True),
        sa.Column('hashed_password', sa.String(), nullable=False),
        sa.Column('full_name', sa.String(), nullable=True),
        sa.Column('status', sa.Enum('active', 'inactive', 'pending', 'blocked', 'deleted', name='user_status_enum'), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('is_superuser', sa.Boolean(), nullable=True),
        sa.Column('notification_enabled', sa.Boolean(), nullable=True),
        sa.Column('webpush_enabled', sa.Boolean(), nullable=True),
        sa.Column('email_notification_enabled', sa.Boolean(), nullable=True),
        sa.Column('quiet_hours_start', sa.Integer(), nullable=True),
        sa.Column('quiet_hours_end', sa.Integer(), nullable=True),
        sa.Column('subscription_info', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('devices', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('timezone', sa.String(), nullable=True),
        sa.Column('language', sa.String(), nullable=True),
        sa.Column('custom_attributes', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('role_id', postgresql.UUID(as_uuid=True), nullable=True),
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
    
    op.create_table('role_permission',
        sa.Column('role_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('permission_name', sa.String(), nullable=False),
        sa.ForeignKeyConstraint(['permission_name'], ['permissions.name'], ),
        sa.ForeignKeyConstraint(['role_id'], ['roles.id'], ),
        sa.PrimaryKeyConstraint('role_id', 'permission_name')
    )
    
    op.create_table('templates',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('body', sa.Text(), nullable=False),
        sa.Column('image_url', sa.String(), nullable=True),
        sa.Column('action_url', sa.String(), nullable=True),
        sa.Column('icon_url', sa.String(), nullable=True),
        sa.Column('template_type', sa.Enum('webpush', 'email', 'sms', 'in_app', 'mobile_push', name='template_type_enum'), nullable=True),
        sa.Column('content', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('variables', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('tags', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('category', sa.String(), nullable=True),
        sa.Column('status', sa.Enum('draft', 'active', 'archived', 'deleted', name='template_status_enum'), nullable=True),
        sa.Column('version', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    op.create_table('campaigns',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('scheduled_time', sa.DateTime(), nullable=True),
        sa.Column('status', sa.Enum('draft', 'scheduled', 'running', 'paused', 'completed', 'cancelled', name='campaign_status_enum'), nullable=True),
        sa.Column('is_recurring', sa.Boolean(), nullable=True),
        sa.Column('recurrence_pattern', sa.String(), nullable=True),
        sa.Column('campaign_type', sa.Enum('one_time', 'recurring', 'trigger_based', 'ab_test', name='campaign_type_enum'), nullable=True),
        sa.Column('segment_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('template_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['segment_id'], ['segments.id'], ),
        sa.ForeignKeyConstraint(['template_id'], ['templates.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    op.create_table('ab_tests',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('campaign_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('variant_count', sa.Integer(), nullable=True),
        sa.Column('winning_criteria', sa.Enum('open_rate', 'click_rate', 'conversion', 'engagement', name='winning_criteria_enum'), nullable=True),
        sa.Column('start_date', sa.DateTime(), nullable=True),
        sa.Column('end_date', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['campaign_id'], ['campaigns.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    op.create_table('cep_decisions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('campaign_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('decision_time', sa.DateTime(), nullable=True),
        sa.Column('selected_channel', sa.String(length=50), nullable=False),
        sa.Column('score', sa.Float(), nullable=False),
        sa.Column('factors', postgresql.JSON(astext_type=sa.Text()), nullable=False),
        sa.Column('alternative_channels', postgresql.JSON(astext_type=sa.Text()), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['campaign_id'], ['campaigns.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    op.create_table('template_versions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('template_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('version', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('body', sa.Text(), nullable=False),
        sa.Column('image_url', sa.String(), nullable=True),
        sa.Column('action_url', sa.String(), nullable=True),
        sa.Column('icon_url', sa.String(), nullable=True),
        sa.Column('content', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
        sa.ForeignKeyConstraint(['template_id'], ['templates.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    op.create_table('test_variants',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('ab_test_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('template_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('sent_count', sa.Integer(), nullable=True),
        sa.Column('opened_count', sa.Integer(), nullable=True),
        sa.Column('clicked_count', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['ab_test_id'], ['ab_tests.id'], ),
        sa.ForeignKeyConstraint(['template_id'], ['templates.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    op.create_table('triggers',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('trigger_type', sa.Enum('event', 'schedule', 'behavior', 'composite', name='trigger_type_enum'), nullable=False),
        sa.Column('status', sa.Enum('active', 'inactive', 'paused', 'error', name='trigger_status_enum'), nullable=True),
        sa.Column('rules', postgresql.JSON(astext_type=sa.Text()), nullable=False),
        sa.Column('schedule', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('action', postgresql.JSON(astext_type=sa.Text()), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('last_triggered_at', sa.DateTime(), nullable=True),
        sa.Column('trigger_count', sa.Integer(), nullable=True),
        sa.Column('error_count', sa.Integer(), nullable=True),
        sa.Column('trigger_metadata', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('cooldown_period', sa.Interval(), nullable=True),
        sa.Column('max_triggers_per_day', sa.Integer(), nullable=True),
        sa.Column('enabled', sa.Boolean(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    op.create_table('notifications',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('campaign_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('template_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('body', sa.Text(), nullable=False),
        sa.Column('image_url', sa.String(), nullable=True),
        sa.Column('action_url', sa.String(), nullable=True),
        sa.Column('personalized_data', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('sent_at', sa.DateTime(), nullable=True),
        sa.Column('delivery_status', sa.Enum('pending', 'queued', 'sending', 'delivered', 'failed', 'opened', 'clicked', name='delivery_status_enum'), nullable=True),
        sa.Column('delivered_at', sa.DateTime(), nullable=True),
        sa.Column('opened_at', sa.DateTime(), nullable=True),
        sa.Column('clicked_at', sa.DateTime(), nullable=True),
        sa.Column('device_info', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('variant_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.ForeignKeyConstraint(['campaign_id'], ['campaigns.id'], ),
        sa.ForeignKeyConstraint(['template_id'], ['templates.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['variant_id'], ['test_variants.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    op.create_table('trigger_executions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('trigger_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('executed_at', sa.DateTime(), nullable=True),
        sa.Column('success', sa.Boolean(), nullable=False),
        sa.Column('action_result', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('error', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['trigger_id'], ['triggers.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    op.create_table('analytics',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('notification_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('campaign_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('delivered', sa.Boolean(), nullable=True),
        sa.Column('opened', sa.Boolean(), nullable=True),
        sa.Column('clicked', sa.Boolean(), nullable=True),
        sa.Column('event_time', sa.DateTime(), nullable=True),
        sa.Column('user_action', sa.String(), nullable=True),
        sa.Column('conversion_type', sa.Enum('purchase', 'signup', 'pageview', 'download', 'custom', name='conversion_type_enum'), nullable=True),
        sa.Column('conversion_value', sa.Float(), nullable=True),
        sa.ForeignKeyConstraint(['campaign_id'], ['campaigns.id'], ),
        sa.ForeignKeyConstraint(['notification_id'], ['notifications.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

def downgrade():
    # Drop tables in reverse order to respect foreign key constraints
    op.drop_table('analytics')
    op.drop_table('trigger_executions')
    op.drop_table('notifications')
    op.drop_table('triggers')
    op.drop_table('test_variants')
    op.drop_table('template_versions')
    op.drop_table('cep_decisions')
    op.drop_table('ab_tests')
    op.drop_table('campaigns')
    op.drop_table('templates')
    op.drop_table('role_permission')
    op.drop_table('users')
    op.drop_table('segments')
    op.drop_table('roles')
    op.drop_table('permissions')
    
    # Drop enums
    op.execute("DROP TYPE user_status_enum;")
    op.execute("DROP TYPE campaign_status_enum;")
    op.execute("DROP TYPE campaign_type_enum;")
    op.execute("DROP TYPE trigger_type_enum;")
    op.execute("DROP TYPE trigger_status_enum;")
    op.execute("DROP TYPE delivery_status_enum;")
    op.execute("DROP TYPE template_type_enum;")
    op.execute("DROP TYPE template_status_enum;")
    op.execute("DROP TYPE segment_type_enum;")
    op.execute("DROP TYPE winning_criteria_enum;")
    op.execute("DROP TYPE conversion_type_enum;")
