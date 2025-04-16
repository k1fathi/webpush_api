#!/bin/bash
set -e

echo "===== Starting Database Migration Script ====="
echo "Current directory: $(pwd)"

# Wait for database to be ready
echo "Waiting for PostgreSQL to be ready..."
/app/scripts/wait-for-it.sh db:5432 -t 60

# Upgrade database to latest migration
echo "Running Alembic migrations..."
alembic upgrade head
ALEMBIC_STATUS=$?

if [ $ALEMBIC_STATUS -eq 0 ]; then
    echo "✅ Alembic migrations applied successfully!"
else
    echo "❌ Error applying Alembic migrations. Status code: $ALEMBIC_STATUS"
    exit 1
fi

# Check database schema
echo "Checking database tables..."
python -c "
import psycopg2
from core.config import settings

try:
    conn = psycopg2.connect(
        host=settings.POSTGRES_SERVER,
        port=settings.POSTGRES_PORT,
        dbname=settings.POSTGRES_DB,
        user=settings.POSTGRES_USER,
        password=settings.POSTGRES_PASSWORD
    )
    
    cursor = conn.cursor()
    cursor.execute(\"\"\"
        SELECT table_name 
        FROM information_schema.tables
        WHERE table_schema = 'public'
        ORDER BY table_name;
    \"\"\")
    
    tables = cursor.fetchall()
    
    if tables:
        print('✅ Database tables found:')
        for table in tables:
            print(f'  - {table[0]}')
    else:
        print('❌ No tables found in the database!')
        
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f'❌ Error checking database: {str(e)}')
    exit(1)
"

echo "===== Database Migration Script Completed ====="