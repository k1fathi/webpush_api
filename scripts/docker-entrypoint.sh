#!/bin/bash
set -e

# Create postgres data directory with correct permissions if it doesn't exist
if [ ! -d "/app/postgres-data" ]; then
    mkdir -p /app/postgres-data
    chmod 777 /app/postgres-data
fi

# Create backup directory with correct permissions if it doesn't exist
if [ ! -d "/app/db_backups" ]; then
    mkdir -p /app/db_backups
    chmod 777 /app/db_backups
fi

# Wait for postgres to be ready
while ! pg_isready -h db -p 5432 -U postgres; do
  echo "Waiting for postgres..."
  sleep 2
done

# Run any startup commands or migrations
echo "Database is ready, running startup commands..."
# Add any other initialization steps here
# For example: alembic upgrade head

# Start the main application
echo "Starting application..."
exec "$@"
