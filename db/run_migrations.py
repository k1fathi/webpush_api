#!/usr/bin/env python3
"""
Database migration script to run Alembic migrations and verify database setup.
Run this script inside the web container.
"""
import os
import sys
import subprocess
import time

def run_command(command):
    """Run a shell command and print output."""
    print(f"\n> Running: {command}")
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    print("Output:")
    print(result.stdout)
    
    if result.stderr:
        print("Errors:")
        print(result.stderr)
    
    return result.returncode

def main():
    """Main function to run migrations and check database."""
    print("=" * 50)
    print("DATABASE MIGRATION TOOL")
    print("=" * 50)
    
    # Wait for database to be ready
    print("\nChecking database connection...")
    db_check_cmd = "python -c 'from core.db import engine; print(\"Database connection successful\")'"
    max_retries = 5
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            result = run_command(db_check_cmd)
            if result == 0:
                print("✅ Database connection established")
                break
        except Exception as e:
            print(f"Connection attempt {retry_count + 1}/{max_retries} failed: {str(e)}")
        
        retry_count += 1
        if retry_count < max_retries:
            print(f"Retrying in 5 seconds...")
            time.sleep(5)
    
    if retry_count >= max_retries:
        print("❌ Failed to connect to database after multiple attempts")
        return 1
    
    # Run Alembic migration
    print("\nRunning Alembic migrations...")
    
    # First check current migration status
    run_command("alembic current")
    
    # Run upgrade to latest version
    result = run_command("alembic upgrade head")
    
    if result != 0:
        print("❌ Migration failed")
        return 1
    
    print("✅ Migration completed successfully")
    
    # Check database tables
    print("\nVerifying database tables...")
    check_tables_cmd = """
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
    exit(1)
"
"""
    run_command(check_tables_cmd)
    
    print("\n" + "=" * 50)
    print("DATABASE MIGRATION COMPLETED")
    print("=" * 50)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())