#!/bin/bash

# Create the postgres data directory if it doesn't exist
mkdir -p ./postgres-data

# Set appropriate permissions
chmod -R 777 ./postgres-data

echo "Postgres data directory is ready."
