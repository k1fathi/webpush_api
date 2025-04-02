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

# Create the webpush_user if it doesn't exist and set password
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

log_message "Database user created/updated successfully"

# Grant permissions
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

log_message "Permissions granted successfully"

log_message "Database initialization completed"
