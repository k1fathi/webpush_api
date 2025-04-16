#!/bin/bash
# Script to run Alembic migrations and capture the output

# Change to the app directory
cd /app

# Run migrations and capture output
echo "Running Alembic migrations at $(date)" > /app/migration_output.txt
echo "----------------------------------------" >> /app/migration_output.txt
alembic current >> /app/migration_output.txt 2>&1
echo "----------------------------------------" >> /app/migration_output.txt
echo "Running upgrade to head..." >> /app/migration_output.txt
alembic upgrade head >> /app/migration_output.txt 2>&1
echo "----------------------------------------" >> /app/migration_output.txt

# List database tables to verify migration
echo "Listing database tables:" >> /app/migration_output.txt
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
    cursor.execute('''
        SELECT table_name 
        FROM information_schema.tables
        WHERE table_schema = 'public'
        ORDER BY table_name;
    ''')
    
    tables = cursor.fetchall()
    
    if tables:
        print('Database tables found:')
        for table in tables:
            print(f'  - {table[0]}')
    else:
        print('No tables found in the database!')
        
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f'Error checking database: {str(e)}')
" >> /app/migration_output.txt 2>&1

echo "Migration process completed. See output in migration_output.txt"