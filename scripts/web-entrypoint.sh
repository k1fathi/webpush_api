#!/bin/bash
set -e

# Set environment variable to auto-create missing migrations
export ALEMBIC_AUTO_CREATE_MISSING=true

# Wait for PostgreSQL
echo "Waiting for PostgreSQL..."
/app/scripts/wait-for-it.sh db:5432 -t 60

# Run migrations
echo "Running database migrations..."
cd /app

# First, check available heads
echo "Checking available migration heads..."
alembic heads

# Upgrade to all heads
echo "Upgrading to all heads..."
alembic upgrade heads

# Start the application
echo "Starting the application..."
exec "$@"