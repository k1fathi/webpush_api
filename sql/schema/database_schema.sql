-- WebPush API Database Schema
-- Generated on April 14, 2025

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create enum types
CREATE TYPE user_status_enum AS ENUM ('active', 'pending', 'inactive', 'suspended');
CREATE TYPE conversion_type_enum AS ENUM ('view', 'click', 'purchase', 'signup', 'custom');
CREATE TYPE campaign_status_enum AS ENUM ('draft', 'scheduled', 'active', 'paused', 'completed', 'cancelled');
CREATE TYPE campaign_type_enum AS ENUM ('one_time', 'recurring', 'triggered', 'ab_test');
CREATE TYPE template_type_enum AS ENUM ('webpush', 'email', 'sms', 'in_app');
CREATE TYPE template_status_enum AS ENUM ('draft', 'active', 'archived', 'deprecated');
CREATE TYPE segment_type_enum AS ENUM ('dynamic', 'static', 'imported');
CREATE TYPE trigger_type_enum AS ENUM ('event', 'schedule', 'api', 'condition');
CREATE TYPE trigger_status_enum AS ENUM ('active', 'paused', 'completed', 'error');
CREATE TYPE cdp_sync_status_enum AS ENUM ('pending', 'in_progress', 'success', 'failed');
CREATE TYPE winning_criteria_enum AS ENUM ('open_rate', 'click_rate', 'conversion', 'engagement');

-- Create Alembic version table
CREATE TABLE IF NOT EXISTS alembic_version (
    version_num VARCHAR(32) NOT NULL,
    CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num)
);

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR NOT NULL UNIQUE,
    username VARCHAR UNIQUE,
    hashed_password VARCHAR NOT NULL,
    full_name VARCHAR,
    status user_status_enum DEFAULT 'pending',
    is_active BOOLEAN DEFAULT TRUE,
    is_superuser BOOLEAN DEFAULT FALSE,
    notification_enabled BOOLEAN DEFAULT TRUE,
    webpush_enabled BOOLEAN DEFAULT TRUE,
    email_notification_enabled BOOLEAN DEFAULT TRUE,
    quiet_hours_start INTEGER,
    quiet_hours_end INTEGER,
    subscription_info JSONB DEFAULT '{}'::jsonb,
    devices JSONB DEFAULT '[]'::jsonb,
    timezone VARCHAR DEFAULT 'UTC',
    language VARCHAR DEFAULT 'en',
    custom_attributes JSONB DEFAULT '{}'::jsonb,
    role_id UUID,
    permissions VARCHAR[],
    last_login TIMESTAMP,
    last_seen TIMESTAMP,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Roles table
CREATE TABLE IF NOT EXISTS roles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR NOT NULL UNIQUE,
    description VARCHAR,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Permissions table
CREATE TABLE IF NOT EXISTS permissions (
    name VARCHAR PRIMARY KEY,
    description VARCHAR,
    category VARCHAR,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Role-Permission association table
CREATE TABLE IF NOT EXISTS role_permission (
    role_id UUID NOT NULL,
    permission_name VARCHAR NOT NULL,
    PRIMARY KEY (role_id, permission_name),
    CONSTRAINT fk_role_permission_roles
        FOREIGN KEY (role_id) REFERENCES roles (id) ON DELETE CASCADE,
    CONSTRAINT fk_role_permission_permissions
        FOREIGN KEY (permission_name) REFERENCES permissions (name) ON DELETE CASCADE
);

-- Segments table
CREATE TABLE IF NOT EXISTS segments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR NOT NULL,
    description TEXT,
    segment_type segment_type_enum DEFAULT 'dynamic',
    filter_criteria JSONB DEFAULT '{}'::jsonb,
    user_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_evaluated_at TIMESTAMP WITH TIME ZONE,
    is_active BOOLEAN DEFAULT TRUE
);

-- User-Segment association table
CREATE TABLE IF NOT EXISTS user_segment (
    user_id UUID NOT NULL,
    segment_id UUID NOT NULL,
    PRIMARY KEY (user_id, segment_id),
    CONSTRAINT fk_user_segment_users
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
    CONSTRAINT fk_user_segment_segments
        FOREIGN KEY (segment_id) REFERENCES segments (id) ON DELETE CASCADE
);

-- Templates table
CREATE TABLE IF NOT EXISTS templates (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR NOT NULL,
    description TEXT,
    title VARCHAR NOT NULL,
    body TEXT NOT NULL,
    image_url VARCHAR,
    action_url VARCHAR,
    icon_url VARCHAR,
    template_type template_type_enum DEFAULT 'webpush',
    content JSONB DEFAULT '{}'::jsonb,
    variables VARCHAR[],
    tags VARCHAR[],
    category VARCHAR,
    status template_status_enum DEFAULT 'draft',
    version INTEGER DEFAULT 1,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by UUID,
    CONSTRAINT fk_templates_users
        FOREIGN KEY (created_by) REFERENCES users (id) ON DELETE SET NULL
);

-- Template versions table
CREATE TABLE IF NOT EXISTS template_versions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    template_id UUID NOT NULL,
    version INTEGER NOT NULL,
    title VARCHAR NOT NULL,
    body TEXT NOT NULL,
    image_url VARCHAR,
    action_url VARCHAR,
    icon_url VARCHAR,
    content JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by UUID,
    CONSTRAINT fk_template_versions_templates
        FOREIGN KEY (template_id) REFERENCES templates (id) ON DELETE CASCADE,
    CONSTRAINT fk_template_versions_users
        FOREIGN KEY (created_by) REFERENCES users (id) ON DELETE SET NULL
);

-- Campaign templates table
CREATE TABLE IF NOT EXISTS campaign_templates (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR NOT NULL,
    description TEXT,
    category VARCHAR NOT NULL,
    status VARCHAR DEFAULT 'draft',
    content JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by UUID,
    CONSTRAINT fk_campaign_templates_users
        FOREIGN KEY (created_by) REFERENCES users (id) ON DELETE SET NULL
);

-- Campaigns table
CREATE TABLE IF NOT EXISTS campaigns (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR NOT NULL,
    description TEXT,
    scheduled_time TIMESTAMP WITH TIME ZONE,
    status campaign_status_enum DEFAULT 'draft',
    is_recurring BOOLEAN DEFAULT FALSE,
    recurrence_pattern VARCHAR,
    campaign_type campaign_type_enum DEFAULT 'one_time',
    segment_id UUID,
    template_id UUID,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    CONSTRAINT fk_campaigns_segments
        FOREIGN KEY (segment_id) REFERENCES segments (id) ON DELETE SET NULL,
    CONSTRAINT fk_campaigns_templates
        FOREIGN KEY (template_id) REFERENCES templates (id) ON DELETE SET NULL
);

-- A/B tests table
CREATE TABLE IF NOT EXISTS ab_tests (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    campaign_id UUID NOT NULL,
    name VARCHAR NOT NULL,
    description TEXT,
    variant_count INTEGER DEFAULT 2,
    winning_criteria winning_criteria_enum DEFAULT 'click_rate',
    start_date TIMESTAMP WITH TIME ZONE,
    end_date TIMESTAMP WITH TIME ZONE,
    CONSTRAINT fk_ab_tests_campaigns
        FOREIGN KEY (campaign_id) REFERENCES campaigns (id) ON DELETE CASCADE
);

-- Test variants table
CREATE TABLE IF NOT EXISTS test_variants (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    ab_test_id UUID NOT NULL,
    template_id UUID NOT NULL,
    name VARCHAR NOT NULL,
    sent_count INTEGER DEFAULT 0,
    opened_count INTEGER DEFAULT 0,
    clicked_count INTEGER DEFAULT 0,
    CONSTRAINT fk_test_variants_ab_tests
        FOREIGN KEY (ab_test_id) REFERENCES ab_tests (id) ON DELETE CASCADE,
    CONSTRAINT fk_test_variants_templates
        FOREIGN KEY (template_id) REFERENCES templates (id) ON DELETE SET NULL
);

-- Notifications table
CREATE TABLE IF NOT EXISTS notifications (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL,
    campaign_id UUID,
    template_id UUID,
    variant_id UUID,
    title VARCHAR NOT NULL,
    body TEXT NOT NULL,
    image_url VARCHAR,
    action_url VARCHAR,
    delivery_status VARCHAR DEFAULT 'pending',
    sent_at TIMESTAMP WITH TIME ZONE,
    delivered_at TIMESTAMP WITH TIME ZONE,
    opened_at TIMESTAMP WITH TIME ZONE,
    clicked_at TIMESTAMP WITH TIME ZONE,
    device_info JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    CONSTRAINT fk_notifications_users
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
    CONSTRAINT fk_notifications_campaigns
        FOREIGN KEY (campaign_id) REFERENCES campaigns (id) ON DELETE SET NULL,
    CONSTRAINT fk_notifications_templates
        FOREIGN KEY (template_id) REFERENCES templates (id) ON DELETE SET NULL,
    CONSTRAINT fk_notifications_variants
        FOREIGN KEY (variant_id) REFERENCES test_variants (id) ON DELETE SET NULL
);

-- Analytics table
CREATE TABLE IF NOT EXISTS analytics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    notification_id UUID,
    campaign_id UUID,
    user_id UUID,
    delivered BOOLEAN DEFAULT FALSE,
    opened BOOLEAN DEFAULT FALSE,
    clicked BOOLEAN DEFAULT FALSE,
    event_time TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    user_action VARCHAR,
    conversion_type conversion_type_enum,
    conversion_value FLOAT DEFAULT 0.0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    CONSTRAINT fk_analytics_notifications
        FOREIGN KEY (notification_id) REFERENCES notifications (id) ON DELETE CASCADE,
    CONSTRAINT fk_analytics_campaigns
        FOREIGN KEY (campaign_id) REFERENCES campaigns (id) ON DELETE CASCADE,
    CONSTRAINT fk_analytics_users
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
);

-- Subscriptions table
CREATE TABLE IF NOT EXISTS subscriptions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID,
    subscription_json TEXT NOT NULL,
    browser VARCHAR,
    device_info JSONB DEFAULT '{}'::jsonb,
    custom_attributes JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_updated TIMESTAMP WITH TIME ZONE,
    CONSTRAINT fk_subscriptions_users
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
);

-- Triggers table
CREATE TABLE IF NOT EXISTS triggers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR NOT NULL,
    description TEXT,
    trigger_type trigger_type_enum NOT NULL,
    status trigger_status_enum DEFAULT 'active',
    rules JSONB NOT NULL,
    schedule JSONB,
    action JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_triggered_at TIMESTAMP WITH TIME ZONE,
    trigger_count INTEGER DEFAULT 0,
    error_count INTEGER DEFAULT 0,
    trigger_metadata JSONB DEFAULT '{}'::jsonb,
    cooldown_period INTERVAL,
    max_triggers_per_day INTEGER,
    enabled BOOLEAN DEFAULT TRUE
);

-- Trigger executions table
CREATE TABLE IF NOT EXISTS trigger_executions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    trigger_id UUID NOT NULL,
    executed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    success BOOLEAN DEFAULT FALSE,
    action_result JSONB,
    error VARCHAR,
    CONSTRAINT fk_trigger_executions_triggers
        FOREIGN KEY (trigger_id) REFERENCES triggers (id) ON DELETE CASCADE
);

-- CDP integrations table
CREATE TABLE IF NOT EXISTS cdp_integrations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL,
    user_profile_data JSONB DEFAULT '{}'::jsonb,
    behavioral_data JSONB DEFAULT '{}'::jsonb,
    last_synced TIMESTAMP WITH TIME ZONE,
    sync_status cdp_sync_status_enum DEFAULT 'pending',
    error_message VARCHAR,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    CONSTRAINT fk_cdp_integrations_users
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
);

-- CEP decisions table
CREATE TABLE IF NOT EXISTS cep_decisions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL,
    campaign_id UUID NOT NULL,
    decision_time TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    selected_channel VARCHAR(50) NOT NULL,
    score FLOAT NOT NULL DEFAULT 0.0,
    factors JSONB NOT NULL DEFAULT '{}'::jsonb,
    alternative_channels JSONB NOT NULL DEFAULT '[]'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    CONSTRAINT fk_cep_decisions_users
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
    CONSTRAINT fk_cep_decisions_campaigns
        FOREIGN KEY (campaign_id) REFERENCES campaigns (id) ON DELETE CASCADE
);

-- Create indexes for better performance
CREATE INDEX idx_users_email ON users (email);
CREATE INDEX idx_users_username ON users (username);
CREATE INDEX idx_notifications_user_id ON notifications (user_id);
CREATE INDEX idx_notifications_campaign_id ON notifications (campaign_id);
CREATE INDEX idx_campaigns_status ON campaigns (status);
CREATE INDEX idx_campaigns_segment_id ON campaigns (segment_id);
CREATE INDEX idx_analytics_notification_id ON analytics (notification_id);
CREATE INDEX idx_analytics_user_id ON analytics (user_id);
CREATE INDEX idx_analytics_campaign_id ON analytics (campaign_id);
CREATE INDEX idx_subscriptions_user_id ON subscriptions (user_id);
CREATE INDEX idx_triggers_name ON triggers (name);
CREATE INDEX idx_triggers_status ON triggers (status);
CREATE INDEX idx_cdp_integrations_user_id ON cdp_integrations (user_id);
CREATE INDEX idx_cep_decisions_user_id ON cep_decisions (user_id);
CREATE INDEX idx_cep_decisions_campaign_id ON cep_decisions (campaign_id);
CREATE INDEX idx_segments_name ON segments (name);
CREATE INDEX idx_templates_name ON templates (name);
CREATE INDEX idx_ab_tests_campaign_id ON ab_tests (campaign_id);