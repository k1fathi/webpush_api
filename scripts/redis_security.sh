#!/bin/bash
set -e

echo "Implementing Redis security hardening..."

# Function to log messages
log_message() {
  echo "$(date +"%Y-%m-%d %H:%M:%S") - $1"
}

# Create Redis configuration with enhanced security
cat > /tmp/redis.conf << EOF
# Redis security configuration
# Basic security settings
protected-mode yes
port 6379
tcp-backlog 511
timeout 0
tcp-keepalive 300

# Authentication
requirepass ${REDIS_PASSWORD:-redis}

# Network security
bind 0.0.0.0
maxclients 10000

# Disable dangerous commands
rename-command FLUSHDB ""
rename-command FLUSHALL ""
rename-command DEBUG ""
rename-command CONFIG ""
rename-command SHUTDOWN ""
rename-command BGSAVE ""
rename-command BGREWRITEAOF ""
rename-command SAVE ""
rename-command KEYS ""
rename-command PEXPIRE ""
rename-command DEL ""

# Memory management
maxmemory-policy allkeys-lru
maxmemory 256mb

# Logging
loglevel notice
logfile ""
EOF

# Check if we can access the Redis configuration directory
if [ -w "/usr/local/etc/redis" ]; then
  cp /tmp/redis.conf /usr/local/etc/redis/redis.conf
  log_message "Redis security configuration installed to /usr/local/etc/redis/redis.conf"
else
  log_message "Cannot access Redis config directory."
  log_message "Manual installation needed - configuration saved to /tmp/redis.conf"
  log_message "Copy this file to your Redis configuration location."
fi

echo "Redis security hardening completed."
