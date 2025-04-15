#!/bin/bash
set -e

echo "Running Postgres data directory initialization..."

# Check if PGDATA directory exists and has content
if [ -z "$(ls -A $PGDATA 2>/dev/null)" ]; then
    echo "PGDATA directory is empty, initializing fresh database..."
else
    echo "PGDATA directory already has content, skipping initialization..."
    exit 0
fi

# Create data directory with proper permissions if needed
DATA_DIR="/var/lib/postgresql/data"
if [ ! -d "$DATA_DIR" ]; then
    echo "Creating data directory at $DATA_DIR"
    mkdir -p "$DATA_DIR"
    chown -R postgres:postgres "$DATA_DIR"
    chmod 700 "$DATA_DIR"
fi

echo "Postgres data directory is ready and will persist across container restarts."
