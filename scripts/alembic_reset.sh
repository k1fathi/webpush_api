#!/bin/bash

# Script to reset the Alembic migration state and database schema
# Use with caution - this will erase your database schema!

# Function to log messages
log_message() {
  echo "$(date +"%Y-%m-%d %H:%M:%S") - $1"
}

log_message "Starting Alembic migration reset"

# Confirm with user
read -p "This will drop and recreate all tables. Are you sure? (y/n): " confirm
if [[ $confirm != [yY] ]]; then
    log_message "Operation cancelled."
    exit 1
fi

# 1. Remove old migrations
log_message "Removing old migration files (except clear_migrations.py)"
find alembic/versions -type f -name "*.py" ! -name "clear_migrations.py" -exec rm -f {} \;

# 2. Reset alembic version
log_message "Deleting alembic_version table from database"
python -c "
from sqlalchemy import create_engine
from core.config import settings
engine = create_engine(settings.SQLALCHEMY_DATABASE_URI)
with engine.connect() as conn:
    conn.execute('DROP TABLE IF EXISTS alembic_version')
    conn.commit()
"

# 3. Run the clear migration
log_message "Running the clear migration"
alembic upgrade head

# 4. Run autogenerate to create a full schema migration
log_message "Auto-generating a complete schema migration"
alembic revision --autogenerate -m "Full schema migration"

# 5. Apply the new migration
log_message "Applying the new migration"
alembic upgrade head

# 6. Verify the current state
log_message "Current migration state:"
alembic current

log_message "Alembic migration reset completed"
