#!/bin/bash
# Script to manage PostgreSQL Docker volume
# Usage: ./postgres_volume_manager.sh [command]
# Commands:
#   backup  - Create a backup of the PostgreSQL volume
#   restore - Restore from a backup
#   status  - Check the status of the PostgreSQL volume
#   clean   - Remove old backups (keeps the 3 most recent)

set -e

# Configuration
VOLUME_NAME="webpush_postgres_data"
BACKUP_DIR="./postgres_backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

# Function to check if the volume exists
check_volume() {
    if ! docker volume ls | grep -q "$VOLUME_NAME"; then
        echo "WARNING: Volume $VOLUME_NAME does not exist yet. It will be created when you start the containers."
        return 1
    fi
    return 0
}

# Function to backup the volume
backup() {
    echo "Creating backup of PostgreSQL volume..."
    
    if ! check_volume; then
        echo "Aborting backup."
        return 1
    fi
    
    echo "Stopping containers that might be using the volume..."
    docker-compose down

    echo "Creating backup archive..."
    BACKUP_FILE="$BACKUP_DIR/postgres_backup_$TIMESTAMP.tar.gz"
    
    # Create a temporary container to access the volume
    docker run --rm -v $VOLUME_NAME:/data -v $(pwd)/$BACKUP_DIR:/backup alpine \
        tar czf /backup/postgres_backup_$TIMESTAMP.tar.gz -C /data .
    
    echo "Backup created at $BACKUP_FILE"
    echo "Restarting containers..."
    docker-compose up -d
}

# Function to restore from a backup
restore() {
    echo "Available backups:"
    ls -1 "$BACKUP_DIR" | grep postgres_backup | sort -r
    
    read -p "Enter backup file name (from the list above): " BACKUP_FILE
    
    if [ ! -f "$BACKUP_DIR/$BACKUP_FILE" ]; then
        echo "Error: Backup file not found!"
        return 1
    fi
    
    echo "Stopping containers..."
    docker-compose down
    
    echo "WARNING: This will overwrite the current database. Are you sure?"
    read -p "Continue (y/n)? " confirm
    if [ "$confirm" != "y" ]; then
        echo "Restore aborted."
        return 1
    fi
    
    echo "Cleaning volume..."
    docker volume rm $VOLUME_NAME || true
    docker volume create $VOLUME_NAME
    
    echo "Restoring from backup..."
    docker run --rm -v $VOLUME_NAME:/data -v $(pwd)/$BACKUP_DIR:/backup alpine \
        sh -c "tar xzf /backup/$BACKUP_FILE -C /data"
    
    echo "Setting correct permissions..."
    docker run --rm -v $VOLUME_NAME:/data alpine \
        sh -c "chown -R 999:999 /data"
    
    echo "Restore completed. Starting containers..."
    docker-compose up -d
}

# Function to check status
status() {
    echo "Checking PostgreSQL volume status..."
    
    if ! check_volume; then
        return 1
    fi
    
    # Get volume information
    echo "Volume information:"
    docker volume inspect $VOLUME_NAME
    
    # Check size of the volume
    echo "Volume size:"
    docker run --rm -v $VOLUME_NAME:/data alpine du -sh /data
    
    # List backups
    echo "Available backups:"
    ls -1 "$BACKUP_DIR" | grep postgres_backup | sort -r
}

# Function to clean old backups
clean() {
    echo "Cleaning old backups (keeping 3 most recent)..."
    ls -1t "$BACKUP_DIR"/postgres_backup_*.tar.gz | tail -n +4 | xargs rm -f
    echo "Cleanup complete."
}

# Main logic
case "$1" in
    backup)
        backup
        ;;
    restore)
        restore
        ;;
    status)
        status
        ;;
    clean)
        clean
        ;;
    *)
        echo "Usage: $0 {backup|restore|status|clean}"
        exit 1
esac

exit 0