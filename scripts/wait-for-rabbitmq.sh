#!/bin/bash
set -e

host="$1"
port="$2"
shift 2

timeout=90
counter=0
step=5

echo "🔄 Waiting for RabbitMQ to be ready on ${host}:${port}..."

until nc -z "$host" "$port"; do
    counter=$((counter + step))
    if [ "$counter" -gt "$timeout" ]; then
        echo "❌ Timed out waiting for RabbitMQ after ${timeout} seconds"
        exit 1
    fi
    echo "⏳ RabbitMQ not ready - retrying in ${step}s (${counter}/${timeout})"
    sleep $step
done

echo "✅ RabbitMQ is ready - executing command"
exec "$@"
