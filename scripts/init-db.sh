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

# Set up schema if needed
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
  CREATE SCHEMA IF NOT EXISTS webpush;
EOSQL

log_message "Schema created successfully"

# Grant permissions (using the same POSTGRES_USER from .env)
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
  GRANT ALL PRIVILEGES ON SCHEMA webpush TO "$POSTGRES_USER";
  GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA webpush TO "$POSTGRES_USER";
  GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA webpush TO "$POSTGRES_USER";
  GRANT ALL PRIVILEGES ON ALL FUNCTIONS IN SCHEMA webpush TO "$POSTGRES_USER";

  -- Allow future tables to be owned by the postgres user
  ALTER DEFAULT PRIVILEGES IN SCHEMA webpush GRANT ALL ON TABLES TO "$POSTGRES_USER";
  ALTER DEFAULT PRIVILEGES IN SCHEMA webpush GRANT ALL ON SEQUENCES TO "$POSTGRES_USER";
  ALTER DEFAULT PRIVILEGES IN SCHEMA webpush GRANT ALL ON FUNCTIONS TO "$POSTGRES_USER";
EOSQL

log_message "Permissions granted successfully"

log_message "Database initialization completed"
