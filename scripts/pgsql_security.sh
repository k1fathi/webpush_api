#!/bin/bash
set -e

echo "Implementing PostgreSQL security hardening..."

# Function to log messages
log_message() {
  echo "$(date +"%Y-%m-%d %H:%M:%S") - $1"
}

# Check if running as postgres user
if [ "$(id -u)" != "$(id -u postgres 2>/dev/null || echo 999)" ]; then
  log_message "WARNING: This script should run as the postgres user."
  log_message "Attempting to continue, but permissions may cause failures."
fi

# Check if data directory is accessible
PG_DATA_DIR="${PGDATA:-/var/lib/postgresql/data}"
if [ ! -w "$PG_DATA_DIR" ]; then
  log_message "ERROR: Cannot write to PostgreSQL data directory: $PG_DATA_DIR"
  log_message "This script will create configuration files in the current directory instead."
  # Create files in current directory so they can be copied later
  PG_DATA_DIR="."
fi

# Create pg_hba.conf with explicit connection rules
cat > "$PG_DATA_DIR/pg_hba.conf.new" << EOF
# TYPE  DATABASE        USER            ADDRESS                 METHOD
local   all             postgres                                peer
host    all             postgres        127.0.0.1/32            md5
host    all             postgres        ::1/128                 md5
host    all             postgres        172.16.0.0/12           md5
host    all             webpush_user    172.16.0.0/12           md5
host    all             all             0.0.0.0/0               reject
EOF

log_message "Created restrictive pg_hba.conf"

# Determine security.conf directory
if [ -d "$PG_DATA_DIR/postgresql.conf.d" ]; then
  CONF_DIR="$PG_DATA_DIR/postgresql.conf.d"
else
  CONF_DIR="$PG_DATA_DIR"
  log_message "postgresql.conf.d directory not found, creating security file in data directory"
fi

# Set PostgreSQL configuration
cat > "$CONF_DIR/security.conf.new" << EOF
# Disable dangerous SQL features
allow_system_table_mods = off
lo_compat_privileges = off

# Prevent SQL injection risks
transform_null_equals = off
backslash_quote = safe_encoding

# Logging and auditing
log_connections = on
log_disconnections = on
log_statement = 'mod'
log_line_prefix = '%t [%p]: [%l-1] user=%u,db=%d,app=%a,client=%h '

# Security settings
password_encryption = scram-sha-256
EOF

log_message "Created security.conf with hardened settings"

# Provide instructions if files were created in current directory
if [ "$PG_DATA_DIR" = "." ]; then
  log_message "Configuration files created in the current directory:"
  log_message "  - $(pwd)/pg_hba.conf.new"
  log_message "  - $(pwd)/security.conf.new"
  log_message ""
  log_message "To apply these settings, run the following as the postgres user:"
  log_message "  cp pg_hba.conf.new /var/lib/postgresql/data/pg_hba.conf"
  log_message "  mkdir -p /var/lib/postgresql/data/postgresql.conf.d/"
  log_message "  cp security.conf.new /var/lib/postgresql/data/postgresql.conf.d/security.conf"
  log_message "  # Or if postgresql.conf.d doesn't exist:"
  log_message "  cp security.conf.new /var/lib/postgresql/data/security.conf"
else
  # Move new files to their proper locations
  mv "$PG_DATA_DIR/pg_hba.conf.new" "$PG_DATA_DIR/pg_hba.conf"
  mv "$CONF_DIR/security.conf.new" "$CONF_DIR/security.conf"
  log_message "Successfully applied security configurations"
fi

echo "PostgreSQL security hardening completed."
