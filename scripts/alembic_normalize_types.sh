#!/bin/bash

set -e

# Function to log messages
log_message() {
  echo "$(date +"%Y-%m-%d %H:%M:%S") - $1"
}

log_message "Starting database type normalization"

# Connect to the database
log_message "Connecting to database..."

# Check if the alembic_version table exists
has_alembic=$(psql -h ${POSTGRES_SERVER} -U ${POSTGRES_USER} -d ${POSTGRES_DB} -t -c "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'alembic_version');")

if [[ $has_alembic == *t* ]]; then
  log_message "Found alembic_version table, removing it to restart migrations"
  psql -h ${POSTGRES_SERVER} -U ${POSTGRES_USER} -d ${POSTGRES_DB} -c "DROP TABLE IF EXISTS alembic_version;"
fi

# Check if tables exist already
has_tables=$(psql -h ${POSTGRES_SERVER} -U ${POSTGRES_USER} -d ${POSTGRES_DB} -t -c "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'users');")

if [[ $has_tables == *t* ]]; then
  log_message "Found existing tables, backing up data before schema changes"
  
  # Create backups of key tables
  tables=("users" "campaigns" "templates" "notifications" "cep_decisions")
  
  for table in "${tables[@]}"; do
    log_message "Backing up $table"
    psql -h ${POSTGRES_SERVER} -U ${POSTGRES_USER} -d ${POSTGRES_DB} -c "CREATE TABLE IF NOT EXISTS ${table}_backup AS SELECT * FROM ${table};"
  done
  
  log_message "Dropping tables in proper order to avoid constraint violations"
  
  psql -h ${POSTGRES_SERVER} -U ${POSTGRES_USER} -d ${POSTGRES_DB} << EOF
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
EOF
fi

# Create a fresh migration
log_message "Creating fresh migration..."
alembic revision --autogenerate -m "Normalized UUID types"

# Apply the migration
log_message "Applying migration..."
alembic upgrade head

log_message "Database schema with normalized UUID types has been created"

# If we had data, we could restore it here with data type conversions
if [[ $has_tables == *t* ]]; then
  log_message "Data was backed up but needs manual restoration due to type changes"
  log_message "Backup tables: users_backup, campaigns_backup, etc."
fi

log_message "Type normalization process completed"
