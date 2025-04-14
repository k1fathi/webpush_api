#!/usr/bin/env python
"""
Script to create all database tables from SQLAlchemy models
This script handles circular dependencies by first creating tables without 
foreign keys, then adding the constraints later.
"""
import sys
import os
import logging
from sqlalchemy import create_engine, inspect, text, MetaData

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from db.base_class import Base
    from core.config import settings
    
    # Import schemas to get enum values
    try:
        from models.schemas.user import UserStatus
        from models.schemas.analytics import ConversionType
        from models.schemas.campaign import CampaignStatus, CampaignType
        logger.info("Successfully imported schema enums")
    except ImportError as e:
        logger.warning(f"Could not import schema enums: {e}")
    
    # Two-phase table creation approach to handle circular dependencies
    def setup_database():
        """Setup the database tables using raw SQL to avoid circular dependencies"""
        try:
            # Get database URL from settings
            db_url = settings.SQLALCHEMY_DATABASE_URI
            
            # Log the database URL (with password masked)
            masked_url = db_url.replace(settings.POSTGRES_PASSWORD, "********") if settings.POSTGRES_PASSWORD else db_url
            logger.info(f"Database URL: {masked_url}")
            
            # Create database engine
            engine = create_engine(db_url)
            
            try:
                with engine.connect() as connection:
                    logger.info("Connected to database successfully!")
                    connection.execution_options(isolation_level="AUTOCOMMIT")
                    
                    # Check existing enum types
                    logger.info("Checking existing enum types...")
                    existing_enums = {}
                    for enum_name in ["user_status_enum", "conversion_type_enum", "campaign_status_enum", "campaign_type_enum"]:
                        try:
                            # Get enum values
                            enum_values_query = text(f"""
                                SELECT e.enumlabel 
                                FROM pg_type t 
                                JOIN pg_enum e ON t.oid = e.enumtypid 
                                WHERE t.typname = '{enum_name}'
                                ORDER BY e.enumsortorder;
                            """)
                            result = connection.execute(enum_values_query)
                            enum_values = [row[0] for row in result]
                            
                            if enum_values:
                                existing_enums[enum_name] = enum_values
                                logger.info(f"  - Found enum {enum_name} with values: {', '.join(enum_values)}")
                            else:
                                logger.info(f"  - Enum {enum_name} not found")
                        except Exception as e:
                            logger.warning(f"  - Error checking enum {enum_name}: {str(e)}")
                    
                    # Execute DDL directly
                    logger.info("Creating database schema...")
                    
                    # Create all tables without foreign keys
                    logger.info("Phase 1: Creating tables without foreign key constraints...")
                    execute_sql_script(connection, create_tables_sql(existing_enums))
                    
                    # Add foreign key constraints
                    logger.info("Phase 2: Adding foreign key constraints...")
                    execute_sql_script(connection, create_foreign_keys_sql())
                    
                    # Verify tables were created
                    inspector = inspect(engine)
                    table_names = inspector.get_table_names()
                    logger.info(f"Successfully created {len(table_names)} tables:")
                    for table_name in sorted(table_names):
                        logger.info(f"  - {table_name}")
                    
                    logger.info("Database setup completed successfully!")
                    return True
            except Exception as e:
                logger.error(f"Database connection or table creation error: {str(e)}")
                return False
            
        except Exception as e:
            logger.error(f"Error setting up database: {str(e)}")
            return False
    
    def execute_sql_script(connection, sql_script):
        """Execute a SQL script with multiple statements"""
        # Split statements by semicolons and execute each one
        statements = sql_script.split(';')
        for statement in statements:
            if statement.strip():
                try:
                    connection.execute(text(statement))
                except Exception as e:
                    logger.error(f"Error executing SQL: {str(e)}")
                    logger.error(f"Failed SQL: {statement}")
                    raise

    def create_tables_sql(existing_enums=None):
        """Generate SQL to create all tables without foreign keys"""
        if existing_enums is None:
            existing_enums = {}
            
        # Use the correct enum values based on what's in the database
        # Default to uppercase if we can't get them from the database
        campaign_status_default = "DRAFT"  # uppercase value from what's in DB
        campaign_type_default = "ONE_TIME"  # uppercase value from what's in DB
        
        # If we have enum values from the database, use those
        if 'campaign_status_enum' in existing_enums and existing_enums['campaign_status_enum']:
            campaign_status_default = existing_enums['campaign_status_enum'][0]
            logger.info(f"Using campaign status default: {campaign_status_default}")
        
        if 'campaign_type_enum' in existing_enums and existing_enums['campaign_type_enum']:
            campaign_type_default = existing_enums['campaign_type_enum'][0]
            logger.info(f"Using campaign type default: {campaign_type_default}")
        
        return f"""
-- Users table
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY,
    email VARCHAR NOT NULL UNIQUE,
    username VARCHAR UNIQUE,
    hashed_password VARCHAR NOT NULL,
    full_name VARCHAR,
    status user_status_enum,
    is_active BOOLEAN DEFAULT TRUE,
    is_superuser BOOLEAN DEFAULT FALSE,
    notification_enabled BOOLEAN DEFAULT TRUE,
    webpush_enabled BOOLEAN DEFAULT TRUE,
    email_notification_enabled BOOLEAN DEFAULT TRUE,
    quiet_hours_start INTEGER,
    quiet_hours_end INTEGER,
    subscription_info JSONB DEFAULT '{{}}'::jsonb,
    devices JSONB DEFAULT '[]'::jsonb,
    timezone VARCHAR DEFAULT 'UTC',
    language VARCHAR DEFAULT 'en',
    custom_attributes JSONB DEFAULT '{{}}'::jsonb,
    role_id UUID,
    permissions VARCHAR[],
    last_login TIMESTAMP,
    last_seen TIMESTAMP,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Roles table
CREATE TABLE IF NOT EXISTS roles (
    id UUID PRIMARY KEY,
    name VARCHAR NOT NULL UNIQUE,
    description VARCHAR,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Permissions table
CREATE TABLE IF NOT EXISTS permissions (
    id UUID PRIMARY KEY,
    name VARCHAR NOT NULL UNIQUE,
    description VARCHAR,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Role-Permission association table
CREATE TABLE IF NOT EXISTS role_permission (
    role_id UUID,
    permission_id UUID,
    PRIMARY KEY (role_id, permission_id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- User-Role association table
CREATE TABLE IF NOT EXISTS user_role (
    user_id UUID,
    role_id UUID,
    PRIMARY KEY (user_id, role_id)
);

-- User-Segment association table
CREATE TABLE IF NOT EXISTS user_segment (
    user_id UUID,
    segment_id UUID,
    PRIMARY KEY (user_id, segment_id)
);

-- Segments table
CREATE TABLE IF NOT EXISTS segments (
    id UUID PRIMARY KEY,
    name VARCHAR NOT NULL,
    description VARCHAR,
    filter_criteria JSONB DEFAULT '{{}}'::jsonb,
    is_active BOOLEAN DEFAULT TRUE,
    created_by UUID,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Templates table
CREATE TABLE IF NOT EXISTS templates (
    id UUID PRIMARY KEY,
    name VARCHAR NOT NULL,
    description VARCHAR,
    content JSONB NOT NULL,
    variables JSONB DEFAULT '[]'::jsonb,
    created_by UUID,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Template versions table
CREATE TABLE IF NOT EXISTS template_versions (
    id UUID PRIMARY KEY,
    template_id UUID,
    version_number INTEGER NOT NULL,
    content JSONB NOT NULL,
    variables JSONB DEFAULT '[]'::jsonb,
    created_by UUID,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Campaigns table
CREATE TABLE IF NOT EXISTS campaigns (
    id UUID PRIMARY KEY,
    name VARCHAR NOT NULL,
    description VARCHAR,
    status campaign_status_enum DEFAULT '{campaign_status_default}',
    campaign_type campaign_type_enum DEFAULT '{campaign_type_default}',
    segment_id UUID,
    schedule JSONB DEFAULT '{{}}'::jsonb,
    start_time TIMESTAMPTZ,
    end_time TIMESTAMPTZ,
    created_by UUID,
    delivery_stats JSONB DEFAULT '{{}}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Campaign-Template association
CREATE TABLE IF NOT EXISTS campaign_templates (
    id UUID PRIMARY KEY,
    campaign_id UUID,
    template_id UUID,
    created_by UUID,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- CDP Integration table
CREATE TABLE IF NOT EXISTS cdp_integrations (
    id UUID PRIMARY KEY,
    name VARCHAR NOT NULL,
    provider VARCHAR NOT NULL,
    config JSONB DEFAULT '{{}}'::jsonb,
    is_active BOOLEAN DEFAULT TRUE,
    created_by UUID,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Notifications table
CREATE TABLE IF NOT EXISTS notifications (
    id UUID PRIMARY KEY,
    user_id UUID,
    campaign_id UUID,
    template_id UUID,
    title VARCHAR NOT NULL,
    body TEXT NOT NULL,
    image_url VARCHAR,
    action_url VARCHAR,
    personalized_data JSONB DEFAULT '{{}}'::jsonb,
    sent_at TIMESTAMPTZ,
    delivery_status VARCHAR DEFAULT 'pending',
    delivered_at TIMESTAMPTZ,
    opened_at TIMESTAMPTZ,
    clicked_at TIMESTAMPTZ,
    device_info JSONB DEFAULT '{{}}'::jsonb,
    variant_id UUID,
    notification_type VARCHAR DEFAULT 'campaign',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- AB Tests table
CREATE TABLE IF NOT EXISTS ab_tests (
    id UUID PRIMARY KEY,
    name VARCHAR NOT NULL,
    description VARCHAR,
    campaign_id UUID,
    winning_variant_id UUID,
    start_time TIMESTAMPTZ,
    end_time TIMESTAMPTZ,
    status VARCHAR DEFAULT 'draft',
    test_criteria JSONB DEFAULT '{{}}'::jsonb,
    created_by UUID,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Test Variants table
CREATE TABLE IF NOT EXISTS test_variants (
    id UUID PRIMARY KEY,
    ab_test_id UUID,
    name VARCHAR NOT NULL,
    description VARCHAR,
    template_id UUID,
    distribution_percentage FLOAT DEFAULT 50.0,
    metrics JSONB DEFAULT '{{}}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Trigger table
CREATE TABLE IF NOT EXISTS triggers (
    id UUID PRIMARY KEY,
    name VARCHAR NOT NULL,
    description VARCHAR,
    event_type VARCHAR NOT NULL,
    condition_type VARCHAR,
    conditions JSONB DEFAULT '{{}}'::jsonb,
    action_type VARCHAR NOT NULL,
    action_data JSONB DEFAULT '{{}}'::jsonb,
    is_active BOOLEAN DEFAULT TRUE,
    created_by UUID,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Trigger Executions table
CREATE TABLE IF NOT EXISTS trigger_executions (
    id UUID PRIMARY KEY,
    trigger_id UUID,
    user_id UUID,
    event_data JSONB DEFAULT '{{}}'::jsonb,
    executed_at TIMESTAMPTZ DEFAULT NOW(),
    success BOOLEAN DEFAULT FALSE,
    error_message VARCHAR,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- CEP Decisions table
CREATE TABLE IF NOT EXISTS cep_decisions (
    id UUID PRIMARY KEY,
    user_id UUID,
    decision_point VARCHAR NOT NULL,
    context JSONB DEFAULT '{{}}'::jsonb,
    decision_result JSONB DEFAULT '{{}}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Analytics table
CREATE TABLE IF NOT EXISTS analytics (
    id UUID PRIMARY KEY,
    notification_id UUID,
    campaign_id UUID,
    user_id UUID,
    delivered BOOLEAN DEFAULT FALSE,
    opened BOOLEAN DEFAULT FALSE,
    clicked BOOLEAN DEFAULT FALSE,
    event_time TIMESTAMPTZ DEFAULT NOW(),
    user_action VARCHAR,
    conversion_type conversion_type_enum,
    conversion_value FLOAT DEFAULT 0.0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Subscriptions table
CREATE TABLE IF NOT EXISTS subscriptions (
    id UUID PRIMARY KEY,
    user_id UUID,
    endpoint VARCHAR NOT NULL,
    p256dh VARCHAR NOT NULL,
    auth VARCHAR NOT NULL,
    user_agent VARCHAR,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
"""

    def create_foreign_keys_sql():
        """Generate SQL to add foreign key constraints"""
        return """
-- Add foreign keys to Users table
ALTER TABLE users ADD CONSTRAINT fk_users_roles
    FOREIGN KEY (role_id) REFERENCES roles (id);

-- Add foreign keys to Role-Permission table
ALTER TABLE role_permission ADD CONSTRAINT fk_role_permission_roles
    FOREIGN KEY (role_id) REFERENCES roles (id) ON DELETE CASCADE;
ALTER TABLE role_permission ADD CONSTRAINT fk_role_permission_permissions
    FOREIGN KEY (permission_id) REFERENCES permissions (id) ON DELETE CASCADE;

-- Add foreign keys to User-Role table
ALTER TABLE user_role ADD CONSTRAINT fk_user_role_users
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE;
ALTER TABLE user_role ADD CONSTRAINT fk_user_role_roles
    FOREIGN KEY (role_id) REFERENCES roles (id) ON DELETE CASCADE;

-- Add foreign keys to User-Segment table
ALTER TABLE user_segment ADD CONSTRAINT fk_user_segment_users
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE;
ALTER TABLE user_segment ADD CONSTRAINT fk_user_segment_segments
    FOREIGN KEY (segment_id) REFERENCES segments (id) ON DELETE CASCADE;

-- Add foreign keys to Segments table
ALTER TABLE segments ADD CONSTRAINT fk_segments_users
    FOREIGN KEY (created_by) REFERENCES users (id) ON DELETE SET NULL;

-- Add foreign keys to Templates table
ALTER TABLE templates ADD CONSTRAINT fk_templates_users
    FOREIGN KEY (created_by) REFERENCES users (id) ON DELETE SET NULL;

-- Add foreign keys to Template Versions table
ALTER TABLE template_versions ADD CONSTRAINT fk_template_versions_templates
    FOREIGN KEY (template_id) REFERENCES templates (id) ON DELETE CASCADE;
ALTER TABLE template_versions ADD CONSTRAINT fk_template_versions_users
    FOREIGN KEY (created_by) REFERENCES users (id) ON DELETE SET NULL;

-- Add foreign keys to Campaigns table
ALTER TABLE campaigns ADD CONSTRAINT fk_campaigns_segments
    FOREIGN KEY (segment_id) REFERENCES segments (id) ON DELETE SET NULL;
ALTER TABLE campaigns ADD CONSTRAINT fk_campaigns_users
    FOREIGN KEY (created_by) REFERENCES users (id) ON DELETE SET NULL;

-- Add foreign keys to Campaign Template table
ALTER TABLE campaign_templates ADD CONSTRAINT fk_campaign_templates_campaigns
    FOREIGN KEY (campaign_id) REFERENCES campaigns (id) ON DELETE CASCADE;
ALTER TABLE campaign_templates ADD CONSTRAINT fk_campaign_templates_templates
    FOREIGN KEY (template_id) REFERENCES templates (id) ON DELETE CASCADE;
ALTER TABLE campaign_templates ADD CONSTRAINT fk_campaign_templates_users
    FOREIGN KEY (created_by) REFERENCES users (id) ON DELETE SET NULL;

-- Add foreign keys to CDP Integration table
ALTER TABLE cdp_integrations ADD CONSTRAINT fk_cdp_integrations_users
    FOREIGN KEY (created_by) REFERENCES users (id) ON DELETE SET NULL;

-- Add foreign keys to Notifications table
ALTER TABLE notifications ADD CONSTRAINT fk_notifications_users
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE;
ALTER TABLE notifications ADD CONSTRAINT fk_notifications_campaigns
    FOREIGN KEY (campaign_id) REFERENCES campaigns (id) ON DELETE SET NULL;
ALTER TABLE notifications ADD CONSTRAINT fk_notifications_templates
    FOREIGN KEY (template_id) REFERENCES templates (id) ON DELETE SET NULL;
ALTER TABLE notifications ADD CONSTRAINT fk_notifications_variants
    FOREIGN KEY (variant_id) REFERENCES test_variants (id) ON DELETE SET NULL;

-- Add foreign keys to AB Tests table
ALTER TABLE ab_tests ADD CONSTRAINT fk_ab_tests_campaigns
    FOREIGN KEY (campaign_id) REFERENCES campaigns (id) ON DELETE CASCADE;
ALTER TABLE ab_tests ADD CONSTRAINT fk_ab_tests_users
    FOREIGN KEY (created_by) REFERENCES users (id) ON DELETE SET NULL;
ALTER TABLE ab_tests ADD CONSTRAINT fk_ab_tests_variants
    FOREIGN KEY (winning_variant_id) REFERENCES test_variants (id) ON DELETE SET NULL;

-- Add foreign keys to Test Variants table
ALTER TABLE test_variants ADD CONSTRAINT fk_test_variants_ab_tests
    FOREIGN KEY (ab_test_id) REFERENCES ab_tests (id) ON DELETE CASCADE;
ALTER TABLE test_variants ADD CONSTRAINT fk_test_variants_templates
    FOREIGN KEY (template_id) REFERENCES templates (id) ON DELETE SET NULL;

-- Add foreign keys to Trigger table
ALTER TABLE triggers ADD CONSTRAINT fk_triggers_users
    FOREIGN KEY (created_by) REFERENCES users (id) ON DELETE SET NULL;

-- Add foreign keys to Trigger Execution table
ALTER TABLE trigger_executions ADD CONSTRAINT fk_trigger_executions_triggers
    FOREIGN KEY (trigger_id) REFERENCES triggers (id) ON DELETE CASCADE;
ALTER TABLE trigger_executions ADD CONSTRAINT fk_trigger_executions_users
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE;

-- Add foreign keys to CEP Decisions table
ALTER TABLE cep_decisions ADD CONSTRAINT fk_cep_decisions_users
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE;

-- Add foreign keys to Analytics table
ALTER TABLE analytics ADD CONSTRAINT fk_analytics_notifications
    FOREIGN KEY (notification_id) REFERENCES notifications (id) ON DELETE CASCADE;
ALTER TABLE analytics ADD CONSTRAINT fk_analytics_campaigns
    FOREIGN KEY (campaign_id) REFERENCES campaigns (id) ON DELETE CASCADE;
ALTER TABLE analytics ADD CONSTRAINT fk_analytics_users
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE;

-- Add foreign keys to Subscriptions table
ALTER TABLE subscriptions ADD CONSTRAINT fk_subscriptions_users
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE;
"""

    if __name__ == "__main__":
        logger.info("Starting database setup...")
        success = setup_database()
        if success:
            logger.info("Database setup completed successfully.")
            sys.exit(0)
        else:
            logger.error("Database setup failed.")
            sys.exit(1)

except ImportError as e:
    logger.error(f"Import error: {str(e)}")
    sys.exit(1)
except Exception as e:
    logger.error(f"Error during setup: {str(e)}")
    sys.exit(1)