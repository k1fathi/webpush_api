#!/bin/bash

# Add a cron job to backup the database daily
(crontab -l 2>/dev/null; echo "0 2 * * * cd /app && python scripts/backup_db.py") | crontab -
echo "Cron job for daily backups has been set up"
