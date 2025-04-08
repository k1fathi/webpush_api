#!/bin/bash
set -e

echo "Starting docker entrypoint script..."

# Debug: Show current user and permissions
echo "Current user: $(whoami)"
echo "Current working directory: $(pwd)"

# Create postgres data directories with more robust permission management
for dir in "/app/postgres-data" "/home/ubuntu/webpush_api/postgres-data" "/app/db_backups"; do
    if [ -d "$dir" ]; then
        echo "Directory $dir exists, ensuring permissions"
        chmod -R 777 "$dir" || echo "Warning: Could not chmod $dir"
    else
        echo "Creating directory $dir"
        mkdir -p "$dir" || echo "Warning: Could not create $dir"
        chmod -R 777 "$dir" || echo "Warning: Could not chmod $dir"
    fi
done

# Try to fix any existing permissions in parent directories
if [ -d "/home/ubuntu/webpush_api" ]; then
    echo "Setting permissions on /home/ubuntu/webpush_api"
    chmod 777 /home/ubuntu/webpush_api || echo "Warning: Could not chmod /home/ubuntu/webpush_api"
fi

# Wait for postgres to be ready
echo "Checking PostgreSQL connection..."
# Increase timeout and add more robust retry logic
timeout=60
start_time=$(date +%s)
until pg_isready -h db -p ${POSTGRES_PORT:-5432} -U postgres; do
    current_time=$(date +%s)
    elapsed=$((current_time - start_time))
    
    if [ $elapsed -gt $timeout ]; then
        echo "Timed out waiting for PostgreSQL after ${timeout} seconds"
        echo "Will proceed anyway and hope for the best"
        break
    fi
    
    echo "PostgreSQL is unavailable - sleeping (${elapsed}s/${timeout}s)"
    sleep 2
done
echo "PostgreSQL check completed - executing command"

# Run any startup commands or migrations if needed
if [ "${RUN_MIGRATIONS}" = "true" ]; then
    echo "Running database migrations..."
    alembic upgrade head || echo "Warning: Migration failed, but continuing"
fi

# Start the main application
echo "Starting application: $@"
exec "$@"
