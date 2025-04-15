#!/bin/bash
set -e

echo "Starting celery worker entrypoint script..."

# Debug: Show current user and permissions
echo "Current user: $(whoami)"
echo "Current working directory: $(pwd)"

# Skip any directory creation or permission changes
# This runs as a non-root user and doesn't need to modify the filesystem

# Wait for postgres to be ready
echo "Checking PostgreSQL connection..."
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

# Check if Redis is available
timeout=30
start_time=$(date +%s)
until nc -z -v -w5 redis 6379; do
    current_time=$(date +%s)
    elapsed=$((current_time - start_time))
    
    if [ $elapsed -gt $timeout ]; then
        echo "Timed out waiting for Redis after ${timeout} seconds"
        echo "Will proceed anyway and hope for the best"
        break
    fi
    
    echo "Redis is unavailable - sleeping (${elapsed}s/${timeout}s)"
    sleep 2
done
echo "Redis check completed"

# Check if RabbitMQ is available
timeout=30
start_time=$(date +%s)
until nc -z -v -w5 rabbitmq 5672; do
    current_time=$(date +%s)
    elapsed=$((current_time - start_time))
    
    if [ $elapsed -gt $timeout ]; then
        echo "Timed out waiting for RabbitMQ after ${timeout} seconds"
        echo "Will proceed anyway and hope for the best"
        break
    fi
    
    echo "RabbitMQ is unavailable - sleeping (${elapsed}s/${timeout}s)"
    sleep 2
done
echo "RabbitMQ check completed"

# Start the celery worker
echo "Starting celery worker: $@"
exec "$@"
