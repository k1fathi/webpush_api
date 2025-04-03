import os
import sys
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context
import logging

# Add the parent directory to the path so we can import from the project
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set up logging
logger = logging.getLogger("alembic")

# This is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

try:
    # Import models and settings more safely
    from db.base_class import Base
    from core.config import settings
    
    # Log database connection info (with password masked)
    connection_str = str(settings.SQLALCHEMY_DATABASE_URI)
    masked_connection = connection_str.replace(settings.POSTGRES_PASSWORD, "********") if settings.POSTGRES_PASSWORD else connection_str
    logger.info(f"Using database connection: {masked_connection}")
    
    # Set the database URL in the Alembic config directly from settings
    # Ensure we are using the correct database URL
    config.set_main_option("sqlalchemy.url", str(settings.SQLALCHEMY_DATABASE_URI))
    
    # Import all models for Alembic to detect
    # These imports cause the models to be registered with Base.metadata
    # You only need to import them, not assign them to variables
    from models.domain.user import UserModel
    from models.domain.role import RoleModel
    from models.domain.permission import PermissionModel
    from models.domain.campaign import CampaignModel
    from models.domain.notification import NotificationModel
    from models.domain.segment import SegmentModel
    from models.domain.template import TemplateModel
    from models.domain.trigger import TriggerModel
    from models.domain.ab_test import AbTestModel
    from models.domain.test_variant import TestVariantModel
    from models.domain.analytics import AnalyticsModel
    from models.domain.cep_decision import CepDecisionModel
    from models.domain.campaign_template import CampaignTemplateModel
    
    # Set the target metadata for Alembic
    target_metadata = Base.metadata
    
    # Print detected tables for debugging
    logger.info("Detected tables:")
    for table in Base.metadata.sorted_tables:
        logger.info(f"  - {table.name}")
    
except ImportError as e:
    logger.error(f"Error importing configuration or models: {e}")
    raise

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,  # Compare column types
        compare_server_default=True  # Compare server defaults
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    # Add error handling for database connection
    try:
        connectable = engine_from_config(
            config.get_section(config.config_ini_section),
            prefix="sqlalchemy.",
            poolclass=pool.NullPool,
        )
        
        with connectable.connect() as connection:
            # Configure Alembic context with our connection and metadata
            context.configure(
                connection=connection, 
                target_metadata=target_metadata,
                compare_type=True,
                compare_server_default=True,
                include_schemas=True,
            )

            # Run the migrations
            try:
                with context.begin_transaction():
                    context.run_migrations()
            except KeyError as e:
                missing_revision = str(e).strip("'")
                logger.error(f"Missing migration '{missing_revision}'. Ensure all migration files are present in 'alembic/versions/'.")
                logger.error("Run `alembic history` to inspect the migration history and verify the missing revision.")
                logger.error("If the migration file is missing, restore it from version control or recreate it manually.")
                logger.error("If the issue persists, consider resetting the database and reapplying migrations.")
                raise
    except Exception as e:
        logger.error(f"Database connection error: {e}")
        # Print more details about configuration
        logger.error(f"Database URL: {masked_connection}")
        logger.error(f"Database server: {settings.POSTGRES_SERVER}")
        logger.error(f"Database name: {settings.POSTGRES_DB}")
        raise

if context.is_offline_mode():
    logger.info("Running migrations in offline mode")
    run_migrations_offline()
else:
    logger.info("Running migrations in online mode")
    run_migrations_online()
