import os
import sys
from logging.config import fileConfig

from sqlalchemy import engine_from_config, create_engine
from sqlalchemy import pool
from pathlib import Path

from alembic import context
import logging

# Add the project root directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the MetaData object from our declarative base
from db.base_class import Base

# Import our models helper to ensure all models are loaded in the correct order
from db.models_helper import load_all_models

# Import our settings module
from core.config import settings

# Load all models to ensure they are registered with Base.metadata
load_all_models()

# Set up logging
logger = logging.getLogger("alembic")

# This is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Set the database URL in the Alembic configuration
config.set_main_option("sqlalchemy.url", settings.SQLALCHEMY_DATABASE_URI)

# Metadata object that contains all table definitions
target_metadata = Base.metadata

try:
    # Log database connection info (with password masked)
    connection_str = str(settings.SQLALCHEMY_DATABASE_URI)
    masked_connection = connection_str.replace(settings.POSTGRES_PASSWORD, "********") if settings.POSTGRES_PASSWORD else connection_str
    logger.info(f"Using database connection: {masked_connection}")
    
    # Print detected tables for debugging
    logger.info("Detected tables:")
    for table in Base.metadata.sorted_tables:
        logger.info(f"  - {table.name}")
    
except ImportError as e:
    logger.error(f"Error importing configuration or models: {e}")
    raise

def create_empty_migration_file(revision_id):
    """Create an empty migration file with the given revision ID."""
    versions_dir = Path(os.path.dirname(__file__)) / "versions"
    versions_dir.mkdir(exist_ok=True)
    
    # Find the latest file in the versions directory to determine dependencies
    existing_files = list(versions_dir.glob("*.py"))
    
    # Default values if we can't determine anything from existing files
    down_revision = None
    depends_on = None
    
    # Try to find the revision that depends on the missing one
    for file_path in existing_files:
        content = file_path.read_text()
        if f"down_revision = '{revision_id}'" in content or f'down_revision = "{revision_id}"' in content:
            # This file depends on our missing migration
            logger.info(f"Found file {file_path.name} that depends on missing revision {revision_id}")
            # Extract the revision of this file to use as the revision our new file upgrades to
            revision_line = [line for line in content.split('\n') if line.strip().startswith('revision = ')][0]
            depends_on = revision_line.split('=')[1].strip().strip("'").strip('"')
            break

    # Create migration file with the missing revision ID
    filename = f"{revision_id}_empty_migration_for_missing_revision.py"
    file_path = versions_dir / filename
    
    # Basic migration file template
    template = f"""
\"\"\"empty migration for missing revision

Revision ID: {revision_id}
Revises: {down_revision or ''}
Create Date: (manually created)

\"\"\"

# revision identifiers, used by Alembic.
revision = '{revision_id}'
down_revision = {repr(down_revision)}
depends_on = {repr(depends_on)}

def upgrade():
    pass

def downgrade():
    pass
"""
    
    file_path.write_text(template)
    logger.info(f"Created empty migration file: {file_path}")
    return file_path

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    # Use the database URL directly from settings
    url = str(settings.SQLALCHEMY_DATABASE_URI)
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    # Create engine directly from settings instead of from config
    try:
        # Create engine directly using settings
        connectable = create_engine(
            str(settings.SQLALCHEMY_DATABASE_URI),
            poolclass=pool.NullPool,
            echo=settings.DB_ECHO_LOG,
            pool_pre_ping=True
        )
        
        with connectable.connect() as connection:
            context.configure(
                connection=connection, 
                target_metadata=target_metadata,
                compare_type=True,
                compare_server_default=True,
                include_schemas=True,
            )

            try:
                with context.begin_transaction():
                    context.run_migrations()
            except KeyError as e:
                missing_revision = str(e).strip("'")
                logger.error(f"Missing migration '{missing_revision}'. Attempting to create an empty migration file.")
                
                # Check if ALEMBIC_AUTO_CREATE_MISSING env var is set
                auto_create = os.environ.get("ALEMBIC_AUTO_CREATE_MISSING", "").lower() in ("true", "1", "yes")
                
                if auto_create:
                    # Create empty migration file
                    create_empty_migration_file(missing_revision)
                    logger.info("Created empty migration file. Please try running 'alembic upgrade head' again.")
                else:
                    logger.error("Set ALEMBIC_AUTO_CREATE_MISSING=true environment variable to automatically create missing migration files.")
                    logger.error("Run `alembic history` to inspect the migration history and verify the missing revision.")
                    logger.error("If the migration file is missing, restore it from version control or recreate it manually.")
                    logger.error("If the issue persists, consider resetting the database and reapplying migrations.")
                    raise
    except Exception as e:
        logger.error(f"Database connection error: {e}")
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
