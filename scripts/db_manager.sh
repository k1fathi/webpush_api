#!/bin/bash

set -e

# Function to log messages
log_message() {
  echo "$(date +"%Y-%m-%d %H:%M:%S") - $1"
}

# Check if psql is available and install if needed
check_dependencies() {
  if ! command -v psql &> /dev/null; then
    log_message "Installing PostgreSQL client..."
    apt-get update && apt-get install -y postgresql-client
  fi
}

# Get current date-time for folder names
DATE_TIME=$(date +"%Y%m%d_%H%M%S")
MIGRATIONS_DIR="/app/alembic/versions"
BACKUPS_DIR="/app/db_backups/${DATE_TIME}"

# Function to initialize database extensions and users
initialize_database() {
  log_message "Running database initialization"
  
  check_dependencies
  
  # Create extensions
  log_message "Creating extensions..."
  PGPASSWORD=${POSTGRES_PASSWORD} psql -h ${POSTGRES_SERVER} -U ${POSTGRES_USER} -d ${POSTGRES_DB} <<-EOSQL
    CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
    CREATE EXTENSION IF NOT EXISTS "hstore";
    CREATE EXTENSION IF NOT EXISTS "pg_trgm";
EOSQL

  # Set up schema
  log_message "Creating schema..."
  psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    CREATE SCHEMA IF NOT EXISTS webpush;
EOSQL

  # Create the webpush_user if it doesn't exist and set password
  log_message "Setting up database user..."
  psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    DO
    \$do\$
    BEGIN
      IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'webpush_user') THEN
        CREATE ROLE webpush_user WITH LOGIN PASSWORD 'postgres';
      END IF;
    END
    \$do\$;

    -- Update password in case user already exists but with wrong password
    ALTER ROLE webpush_user WITH PASSWORD 'postgres';
EOSQL

  # Grant permissions
  log_message "Granting permissions..."
  psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    -- Grant permissions to primary user
    GRANT ALL PRIVILEGES ON DATABASE "$POSTGRES_DB" TO "$POSTGRES_USER";
    GRANT ALL PRIVILEGES ON SCHEMA webpush TO "$POSTGRES_USER";
    GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA webpush TO "$POSTGRES_USER";
    GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA webpush TO "$POSTGRES_USER";
    GRANT ALL PRIVILEGES ON ALL FUNCTIONS IN SCHEMA webpush TO "$POSTGRES_USER";
    
    -- Grant permissions to webpush_user
    GRANT CONNECT ON DATABASE "$POSTGRES_DB" TO webpush_user;
    GRANT USAGE ON SCHEMA webpush TO webpush_user;
    GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA webpush TO webpush_user;
    GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA webpush TO webpush_user;
    GRANT ALL PRIVILEGES ON ALL FUNCTIONS IN SCHEMA webpush TO webpush_user;

    -- Allow future tables to have appropriate permissions
    ALTER DEFAULT PRIVILEGES IN SCHEMA webpush 
    GRANT ALL ON TABLES TO "$POSTGRES_USER";
    
    ALTER DEFAULT PRIVILEGES IN SCHEMA webpush 
    GRANT ALL ON TABLES TO webpush_user;
    
    ALTER DEFAULT PRIVILEGES IN SCHEMA webpush 
    GRANT ALL ON SEQUENCES TO "$POSTGRES_USER";
    
    ALTER DEFAULT PRIVILEGES IN SCHEMA webpush 
    GRANT ALL ON SEQUENCES TO webpush_user;
EOSQL

  log_message "Database initialization completed"
}

# Function to backup existing data
backup_data() {
  log_message "Backing up existing data"
  
  check_dependencies
  
  # Create backup directory
  mkdir -p $BACKUPS_DIR
  
  # Check if tables exist
  has_tables=$(PGPASSWORD=${POSTGRES_PASSWORD} psql -h ${POSTGRES_SERVER} -U ${POSTGRES_USER} -d ${POSTGRES_DB} -t -c "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'users');")
  
  if [[ $has_tables == *t* ]]; then
    log_message "Found existing tables, creating backups"
    
    # Tables to backup
    tables=("users" "campaigns" "templates" "notifications" "cep_decisions" "roles" "permissions" "segments")
    
    for table in "${tables[@]}"; do
      if psql -h ${POSTGRES_SERVER} -U ${POSTGRES_USER} -d ${POSTGRES_DB} -c "\dt ${table}" &>/dev/null; then
        log_message "Backing up table: ${table}"
        
        # Create SQL dump
        pg_dump -h ${POSTGRES_SERVER} -U ${POSTGRES_USER} -d ${POSTGRES_DB} -t ${table} > "${BACKUPS_DIR}/${table}.sql"
        
        # Also create a CSV backup
        psql -h ${POSTGRES_SERVER} -U ${POSTGRES_USER} -d ${POSTGRES_DB} -c "COPY ${table} TO '${BACKUPS_DIR}/${table}.csv' WITH CSV HEADER;"
      else
        log_message "Table ${table} does not exist, skipping"
      fi
    done
    
    log_message "Data backup completed to ${BACKUPS_DIR}"
  else
    log_message "No existing tables to backup"
  fi
}

# Function to reset alembic state
reset_alembic() {
  log_message "Resetting Alembic state"
  
  check_dependencies
  
  # Drop the alembic_version table
  PGPASSWORD=${POSTGRES_PASSWORD} psql -h ${POSTGRES_SERVER} -U ${POSTGRES_USER} -d ${POSTGRES_DB} -c "DROP TABLE IF EXISTS alembic_version;"
  
  # Create migrations directory for this run
  VERSION_DIR="${MIGRATIONS_DIR}/${DATE_TIME}"
  mkdir -p $VERSION_DIR
  
  # Create a symlink for alembic to find migrations
  if [ -d "${MIGRATIONS_DIR}/current" ]; then
    rm -f "${MIGRATIONS_DIR}/current"
  fi
  ln -s $VERSION_DIR "${MIGRATIONS_DIR}/current"
  
  log_message "Alembic state reset complete"
}

# Function to drop existing tables
drop_tables() {
  log_message "Dropping existing tables"
  
  check_dependencies
  
  PGPASSWORD=${POSTGRES_PASSWORD} psql -h ${POSTGRES_SERVER} -U ${POSTGRES_USER} -d ${POSTGRES_DB} << EOF
    DROP TABLE IF EXISTS analytics CASCADE;
    DROP TABLE IF EXISTS cep_decisions CASCADE;
    DROP TABLE IF EXISTS notifications CASCADE;
    DROP TABLE IF EXISTS trigger_executions CASCADE;
    DROP TABLE IF EXISTS triggers CASCADE;
    DROP TABLE IF EXISTS test_variants CASCADE;
    DROP TABLE IF EXISTS template_versions CASCADE;
    DROP TABLE IF EXISTS ab_tests CASCADE;
    DROP TABLE IF EXISTS campaigns CASCADE;
    DROP TABLE IF EXISTS templates CASCADE;
    DROP TABLE IF EXISTS user_segment CASCADE;
    DROP TABLE IF EXISTS user_role CASCADE;
    DROP TABLE IF EXISTS role_permission CASCADE;
    DROP TABLE IF EXISTS users CASCADE;
    DROP TABLE IF EXISTS segments CASCADE;
    DROP TABLE IF EXISTS roles CASCADE;
    DROP TABLE IF EXISTS permissions CASCADE;

    DROP TYPE IF EXISTS user_status_enum CASCADE;
    DROP TYPE IF EXISTS campaign_status_enum CASCADE;
    DROP TYPE IF EXISTS campaign_type_enum CASCADE;
    DROP TYPE IF EXISTS trigger_type_enum CASCADE;
    DROP TYPE IF EXISTS trigger_status_enum CASCADE;
    DROP TYPE IF EXISTS delivery_status_enum CASCADE;
    DROP TYPE IF EXISTS template_type_enum CASCADE;
    DROP TYPE IF EXISTS template_status_enum CASCADE;
    DROP TYPE IF EXISTS segment_type_enum CASCADE;
    DROP TYPE IF EXISTS winning_criteria_enum CASCADE;
    DROP TYPE IF EXISTS conversion_type_enum CASCADE;
EOF

  log_message "Tables dropped successfully"
}

# Function to create a fresh migration
create_migration() {
  migration_name=$1
  log_message "Creating migration: ${migration_name}"
  
  # First check if the database is up to date
  log_message "Checking database status..."
  current_revision=$(alembic current 2>/dev/null || echo "None")
  
  # If there's a "not up to date" message or no current revision, upgrade first
  if [[ "$current_revision" == *"not up to date"* || "$current_revision" == "None" ]]; then
    log_message "Database is not up to date, upgrading first..."
    apply_migrations
  fi
  
  # Now create the migration
  log_message "Creating new migration..."
  alembic revision --autogenerate -m "${migration_name}" || {
    log_status=$?
    log_message "Error creating migration (status code: $log_status)"
    
    # If there's still an issue, try to provide more info
    log_message "Checking migration heads..."
    alembic heads || log_message "Could not determine migration heads"
    
    # Return the error status
    return $log_status
  }
  
  # Migration created successfully
  log_message "Migration created successfully"
}

# Function to apply migrations
apply_migrations() {
  log_message "Applying migrations"
  
  # Apply the migrations
  alembic upgrade head || {
    log_status=$?
    log_message "Error applying migrations (status code: $log_status)"
    
    # Try to provide more info
    log_message "Checking migration status..."
    alembic current || log_message "Could not determine migration status"
    
    # Return the error status
    return $log_status
  }
  
  log_message "Displaying current migration state"
  alembic current
}

# Function for a complete DB reset
complete_reset() {
  log_message "Starting complete database reset"
  
  backup_data
  reset_alembic
  drop_tables
  initialize_database
  create_migration "fresh_schema_${DATE_TIME}"
  apply_migrations
  
  log_message "Complete reset finished"
}

# Function to fix multiple migration heads
fix_migration_heads() {
  log_message "Fixing multiple migration heads"
  
  # Get current heads
  log_message "Current migration heads:"
  alembic heads || log_message "No migration heads found"
  
  # Create a merge migration
  log_message "Creating merge migration"
  alembic revision --autogenerate -m "merge_heads_${DATE_TIME}"
  
  # Apply the merge
  log_message "Applying merge migration"
  alembic upgrade heads || log_message "Error applying merge migration"
  
  log_message "Migration heads fixed"
}

# Main execution - add dependency check
check_dependencies

case "$1" in
  init)
    initialize_database
    ;;
  backup)
    backup_data
    ;;
  reset-alembic)
    reset_alembic
    ;;
  drop-tables)
    if [[ "$2" == "--force" ]]; then
      drop_tables
    else
      read -p "This will drop all tables. Are you sure? (y/n): " confirm
      if [[ $confirm == [yY] ]]; then
        drop_tables
      else
        log_message "Operation cancelled"
      fi
    fi
    ;;
  new-migration)
    migration_name=${2:-"migration_${DATE_TIME}"}
    create_migration "$migration_name"
    ;;
  upgrade)
    apply_migrations
    ;;
  fix-heads)
    fix_migration_heads
    ;;
  full-reset)
    if [[ "$2" == "--force" ]]; then
      complete_reset
    else
      read -p "This will perform a full database reset. All data will be lost. Are you sure? (y/n): " confirm
      if [[ $confirm == [yY] ]]; then
        complete_reset
      else
        log_message "Operation cancelled"
      fi
    fi
    ;;
  sync-and-migrate)
    migration_name=${2:-"migration_${DATE_TIME}"}
    log_message "Syncing database and creating migration: ${migration_name}"
    apply_migrations && create_migration "$migration_name"
    ;;
  *)
    echo "Usage: $0 {init|backup|reset-alembic|drop-tables|new-migration|upgrade|fix-heads|full-reset|sync-and-migrate} [options]"
    echo ""
    echo "Commands:"
    echo "  init              Initialize database with extensions and permissions"
    echo "  backup            Backup existing data to SQL and CSV files"
    echo "  reset-alembic     Reset the Alembic migration state"
    echo "  drop-tables       Drop all database tables (use --force to skip confirmation)"
    echo "  new-migration     Create a new migration (optionally provide name as second argument)"
    echo "  upgrade           Apply all pending migrations"
    echo "  fix-heads         Fix multiple migration heads"
    echo "  full-reset        Perform a full database reset (use --force to skip confirmation)"
    echo "  sync-and-migrate  Apply migrations and then create a new one (for out-of-sync databases)"
    echo ""
    echo "Example: $0 init"
    echo "Example: $0 new-migration add_user_preferences"
    echo "Example: $0 sync-and-migrate user_profile_fields"
    echo "Example: $0 full-reset --force"
    exit 1
    ;;
esac

log_message "Script execution completed"
exit 0
