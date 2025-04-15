#!/bin/bash
set -e

echo "Starting docker entrypoint script..."

# Debug: Show current user and permissions
echo "Current user: $(whoami)"
echo "Current working directory: $(pwd)"

# Only try to modify directories if SKIP_PERMISSION_CHECKS is not set
if [ "$SKIP_PERMISSION_CHECKS" != "true" ]; then
    # Check if directories exist before trying to change permissions
    for dir in "/app/db_backups"; do
        if [ -d "$dir" ]; then
            echo "Directory $dir exists, ensuring permissions"
            chmod -R 777 "$dir" 2>/dev/null || echo "Warning: Could not chmod $dir"
        else
            echo "Creating directory $dir"
            mkdir -p "$dir" 2>/dev/null || echo "Warning: Could not create $dir"
            chmod -R 777 "$dir" 2>/dev/null || echo "Warning: Could not chmod $dir"
        fi
    done

    # Create static files directory if it doesn't exist
    if [ ! -d "/app/static" ]; then
        echo "Creating static directory for FastAPI static files"
        mkdir -p /app/static 2>/dev/null || echo "Warning: Could not create /app/static"
        chmod -R 755 /app/static 2>/dev/null || echo "Warning: Could not chmod /app/static"
        # Create a placeholder file to ensure the directory isn't empty
        echo "This is a placeholder file for the static directory" > /app/static/placeholder.txt 2>/dev/null || echo "Warning: Could not create placeholder file"
    fi

    # Ensure static directory exists with proper permissions
    mkdir -p /app/static/js 2>/dev/null || echo "Warning: Could not create /app/static/js"
    chmod -R 777 /app/static 2>/dev/null || echo "Warning: Could not chmod /app/static"
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

# Check if Postgres is available
until nc -z -v -w30 db 5432
do
  echo "Waiting for database connection..."
  sleep 2
done
echo "Database is ready!"

# Run any startup commands or migrations if needed
if [ "${RUN_MIGRATIONS}" = "true" ]; then
    echo "Running database migrations..."
    alembic upgrade head || echo "Warning: Migration failed, but continuing"
fi

# Verify if uvicorn is available when needed
if [[ "$*" == *"uvicorn"* ]]; then
    if ! command -v uvicorn &> /dev/null; then
        echo "Error: uvicorn command not found. Installing required packages..."
        pip install --no-cache-dir uvicorn fastapi || echo "Failed to install uvicorn"
    fi
fi

# Start the main application
echo "Starting application: $@"
exec "$@"
