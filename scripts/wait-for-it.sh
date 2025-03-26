#!/bin/bash

set -e

host="$1"
port="$2"
shift 2
cmd="$@"

timeout=90
counter=0
step=5

echo "🔄 Waiting for PostgreSQL to be ready on ${host}:${port}..."

# First wait for PostgreSQL to accept connections
until PGPASSWORD=$POSTGRES_PASSWORD psql -h "$host" -U "$POSTGRES_USER" -d "postgres" -c '\l' > /dev/null 2>&1; do
    counter=$((counter + step))
    if [ "$counter" -gt "$timeout" ]; then
        echo "❌ Timed out waiting for PostgreSQL after ${timeout} seconds"
        exit 1
    fi
    echo "⏳ PostgreSQL server not ready - retrying in ${step}s (${counter}/${timeout})"
    sleep $step
done

echo "✅ PostgreSQL server is accepting connections"

# Then wait for our specific database to be ready
counter=0
until PGPASSWORD=$POSTGRES_PASSWORD psql -h "$host" -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c 'SELECT 1' > /dev/null 2>&1; do
    counter=$((counter + step))
    if [ "$counter" -gt "$timeout" ]; then
        echo "❌ Timed out waiting for database ${POSTGRES_DB} after ${timeout} seconds"
        exit 1
    fi
    echo "⏳ Database ${POSTGRES_DB} not ready - waiting ${step}s (${counter}/${timeout})"
    sleep $step
done

echo "✅ Database ${POSTGRES_DB} is ready - executing command"
exec $cmd
