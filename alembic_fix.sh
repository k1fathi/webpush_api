#!/bin/bash

# Helper script to fix Alembic multiple heads issue

# Function to log messages
log_message() {
  echo "$(date +"%Y-%m-%d %H:%M:%S") - $1"
}

log_message "Starting Alembic migration fix"

# 1. Show current revision heads
log_message "Current revision heads:"
alembic heads

# 2. Apply migrations to heads (all separate branches)
log_message "Applying migrations to all heads"
alembic upgrade heads

# 3. Apply the merge migration
log_message "Applying merge migration"
alembic upgrade merge_heads_migration

# 4. Verify the current state
log_message "Current state after merge:"
alembic current

log_message "Alembic migration fix completed"
