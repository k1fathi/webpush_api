#!/bin/bash
# Script to run database connection tests

# Change to the project root directory
cd "$(dirname "$0")/.."

# Check if running in Docker or locally
if [ -f "/.dockerenv" ]; then
    echo "Running in Docker environment"
    python scripts/test_db_connection.py
else
    echo "Running in local environment"
    # Check if virtual environment exists
    if [ -d ".venv" ]; then
        echo "Using virtual environment"
        source .venv/bin/activate || source .venv/Scripts/activate
    fi
    python scripts/test_db_connection.py
fi

# Exit with the same exit code as the test script
exit $?
