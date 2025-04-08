#!/bin/bash
set -e

# Create postgres data directory with correct permissions if it doesn't exist
mkdir -p /app/postgres-data
chmod -R 777 /app/postgres-data

# Create backup directory with correct permissions if it doesn't exist
mkdir -p /app/db_backups
chmod -R 777 /app/db_backups

# Wait for postgres to be ready
echo "Checking PostgreSQL connection..."
until pg_isready -h db -p ${POSTGRES_PORT:-5432} -U postgres; do
  echo "PostgreSQL is unavailable - sleeping"
  sleep 1
done
echo "PostgreSQL is up - executing command"

# Run any startup commands or migrations if needed
if [ "${RUN_MIGRATIONS}" = "true" ]; then
  echo "Running database migrations..."
  alembic upgrade head
fi

# Start the main application
echo "Starting application..."
exec "$@"
