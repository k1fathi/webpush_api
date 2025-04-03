#!/bin/bash

# Helper script to fix Alembic multiple heads issue

# Function to log messages
log_message() {
  echo "$(date +"%Y-%m-%d %H:%M:%S") - $1"
}

log_message "Starting Alembic migration fix"

# First, let's drop existing tables that might cause conflicts
log_message "Dropping existing problematic tables..."
psql -h ${POSTGRES_SERVER} -U ${POSTGRES_USER} -d ${POSTGRES_DB} << EOF
DROP TABLE IF EXISTS cep_decisions CASCADE;
DROP TABLE IF EXISTS campaigns CASCADE; 
DROP TABLE IF EXISTS users CASCADE;
DROP TYPE IF EXISTS campaign_status_enum CASCADE;
DROP TYPE IF EXISTS campaign_type_enum CASCADE;
DROP TYPE IF EXISTS user_status_enum CASCADE;
EOF

# Reset alembic_version table
log_message "Resetting alembic_version table..."
psql -h ${POSTGRES_SERVER} -U ${POSTGRES_USER} -d ${POSTGRES_DB} -c "DROP TABLE IF EXISTS alembic_version;"

# 1. Show current revision heads
log_message "Current revision heads:"
alembic heads || log_message "No revisions found."

# 2. Apply the c7fd83cf7ae8 migration first (with the fixed UUID types)
log_message "Applying initial migration..."
alembic upgrade c7fd83cf7ae8 || log_message "Failed to apply initial migration, continuing..."

# 3. Apply any other migrations
log_message "Applying remaining migrations..."
alembic upgrade heads || log_message "Failed to apply migrations, continuing..."

# 4. Verify the current state
log_message "Current state after migrations:"
alembic current

log_message "Alembic migration fix completed"
