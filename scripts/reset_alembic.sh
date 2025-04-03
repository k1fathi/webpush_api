#!/bin/bash

set -e

# Function to log messages
log_message() {
  echo "$(date +"%Y-%m-%d %H:%M:%S") - $1"
}

log_message "Starting complete Alembic reset"

# 1. Drop the alembic_version table to reset migration tracking
log_message "Dropping alembic_version table..."
psql -h ${POSTGRES_SERVER} -U ${POSTGRES_USER} -d ${POSTGRES_DB} -c "DROP TABLE IF EXISTS alembic_version;"

# 2. Remove all existing migrations except the clear_migrations.py
log_message "Removing existing migration files..."
find /app/alembic/versions -type f -name "*.py" ! -name "clear_migrations.py" -exec rm -f {} \;

# 3. Create a fresh migration file
log_message "Creating a fresh migration..."
alembic revision --autogenerate -m "Fresh migration with UUID types"

log_message "Migration reset complete. Next steps:"
log_message "1. Edit the new migration file to ensure all types are correct"
log_message "2. Run 'alembic upgrade head' to apply the new migration"
