#!/bin/bash

# Script to fix Alembic multiple heads issue
# This script will merge multiple heads into a single revision

set -e

# Function to log messages
log_message() {
  echo "$(date +"%Y-%m-%d %H:%M:%S") - $1"
}

log_message "Starting Alembic migration heads fix"

# Check if we have multiple heads
log_message "Checking for multiple migration heads"
heads_output=$(alembic heads)
log_message "Current heads: $heads_output"

# Process heads output to extract revision IDs
revisions=$(echo "$heads_output" | grep -E "^[0-9a-f]+" | awk '{print $1}')
revision_count=$(echo "$revisions" | wc -l)

if [ "$revision_count" -le 1 ]; then
  log_message "No multiple heads detected, nothing to fix"
  exit 0
fi

log_message "Found $revision_count migration heads"

# Create a merge migration
merge_name="merge_heads_$(date +%Y%m%d_%H%M%S)"
log_message "Creating merge migration: $merge_name"

alembic revision --autogenerate -m "$merge_name"

# Apply the merge migration
log_message "Applying merge migration"
alembic upgrade heads

# Check if the merge was successful
log_message "Checking migration state after merge"
current_revision=$(alembic current)
log_message "Current revision: $current_revision"

# Verify we now have a single head
heads_output=$(alembic heads)
revision_count=$(echo "$heads_output" | grep -E "^[0-9a-f]+" | wc -l)

if [ "$revision_count" -le 1 ]; then
  log_message "Migration heads successfully merged"
else
  log_message "Warning: Still have multiple heads after merge operation"
  log_message "You may need to run this script again or fix manually"
fi

log_message "Migration heads fix completed"
