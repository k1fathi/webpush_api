#!/bin/bash
set -e

# Function to log messages
log_message() {
  echo "$(date +"%Y-%m-%d %H:%M:%S") - $1"
}

log_message "Running database initialization script"

# Create extensions
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
  CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
  CREATE EXTENSION IF NOT EXISTS "hstore";
  CREATE EXTENSION IF NOT EXISTS "pg_trgm";
EOSQL

log_message "Database extensions created successfully"

log_message "Database initialization completed"
