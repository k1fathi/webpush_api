#!/usr/bin/env python
"""
Database Connection and Schema Validation Test Script

This script tests:
1. Connection to the database
2. Validates all expected tables exist
3. Performs basic CRUD operations to ensure database functionality
"""

import os
import sys
import time
import logging
from pathlib import Path
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.exc import SQLAlchemyError
import asyncio
import asyncpg

# Add the parent directory to the path so we can import from the project
sys.path.append(str(Path(__file__).parent.parent))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger("db-test")

# Import settings from the project
try:
    from core.config import settings
    from db.base_class import Base
    
    # Import all models to ensure they're registered with SQLAlchemy
    from models.domain.user import UserModel
    from models.domain.role import RoleModel
    from models.domain.permission import PermissionModel
    # ...other model imports
except ImportError as e:
    logger.error(f"Failed to import required modules: {e}")
    sys.exit(1)

async def test_asyncpg_connection():
    """Test connection using asyncpg (for FastAPI/async usage)"""
    logger.info("Testing asyncpg connection...")
    
    try:
        # Create PostgreSQL connection string for asyncpg
        # Format: postgresql://user:password@host:port/database
        db_url = str(settings.SQLALCHEMY_DATABASE_URI)
        if db_url.startswith('postgresql+asyncpg://'):
            db_url = db_url.replace('postgresql+asyncpg://', 'postgresql://')
        
        conn = await asyncpg.connect(db_url)
        logger.info("✅ Successfully connected to database with asyncpg")
        
        # Test a simple query
        version = await conn.fetchval('SELECT version();')
        logger.info(f"PostgreSQL version: {version}")
        
        await conn.close()
        return True
    except Exception as e:
        logger.error(f"❌ asyncpg connection failed: {e}")
        return False

def test_sqlalchemy_connection():
    """Test connection using SQLAlchemy"""
    logger.info("Testing SQLAlchemy connection...")
    
    try:
        # Create SQLAlchemy engine
        engine = create_engine(
            str(settings.SQLALCHEMY_DATABASE_URI).replace('+asyncpg', ''),
            echo=False,
            pool_pre_ping=True
        )
        
        # Test connection
        with engine.connect() as connection:
            logger.info("✅ Successfully connected to database with SQLAlchemy")
            
            # Get database version
            result = connection.execute(text("SELECT version();"))
            version = result.scalar()
            logger.info(f"PostgreSQL version: {version}")
        
        return engine
    except SQLAlchemyError as e:
        logger.error(f"❌ SQLAlchemy connection failed: {e}")
        return None

def validate_tables(engine):
    """Validate all expected tables exist in the database"""
    logger.info("Validating database tables...")
    
    if not engine:
        logger.error("Cannot validate tables: No engine provided")
        return False
    
    try:
        inspector = inspect(engine)
        existing_tables = set(inspector.get_table_names())
        
        # Get expected tables from SQLAlchemy metadata
        expected_tables = set(Base.metadata.tables.keys())
        
        logger.info(f"Found {len(existing_tables)} tables in database")
        
        # Check for missing tables
        missing_tables = expected_tables - existing_tables
        if missing_tables:
            logger.error(f"❌ Missing tables: {', '.join(missing_tables)}")
            return False
        
        # Log all found tables
        logger.info("Tables found in database:")
        for table in sorted(existing_tables):
            columns = [col['name'] for col in inspector.get_columns(table)]
            logger.info(f"  - {table}: {', '.join(columns[:5])}{'...' if len(columns) > 5 else ''}")
        
        logger.info("✅ All expected tables exist in the database")
        return True
    except Exception as e:
        logger.error(f"❌ Error validating tables: {e}")
        return False

def test_basic_crud(engine):
    """Test basic CRUD operations on the database"""
    logger.info("Testing basic CRUD operations...")
    
    if not engine:
        logger.error("Cannot test CRUD: No engine provided")
        return False
    
    test_table = "db_test_table"
    
    try:
        # Create a test table
        with engine.begin() as conn:
            conn.execute(text(f"""
                CREATE TABLE IF NOT EXISTS {test_table} (
                    id SERIAL PRIMARY KEY,
                    name TEXT,
                    created_at TIMESTAMP DEFAULT NOW()
                )
            """))
            
            # Insert a test record
            conn.execute(text(f"""
                INSERT INTO {test_table} (name) VALUES ('test_record')
            """))
            
            # Query the test record
            result = conn.execute(text(f"SELECT * FROM {test_table}"))
            record = result.fetchone()
            logger.info(f"Test record: {record}")
            
            # Update the test record
            conn.execute(text(f"""
                UPDATE {test_table} SET name = 'updated_test_record' WHERE id = :id
            """), {"id": record[0]})
            
            # Query the updated record
            result = conn.execute(text(f"SELECT * FROM {test_table} WHERE id = :id"), {"id": record[0]})
            updated_record = result.fetchone()
            logger.info(f"Updated record: {updated_record}")
            
            # Delete the test record
            conn.execute(text(f"DELETE FROM {test_table} WHERE id = :id"), {"id": record[0]})
            
            # Clean up - drop the test table
            conn.execute(text(f"DROP TABLE {test_table}"))
        
        logger.info("✅ Basic CRUD operations successful")
        return True
    except Exception as e:
        logger.error(f"❌ Error testing CRUD operations: {e}")
        return False

async def main():
    """Main test function"""
    logger.info("Starting database connection and validation tests")
    logger.info(f"Database URL: {str(settings.SQLALCHEMY_DATABASE_URI).replace(settings.POSTGRES_PASSWORD, '********')}")
    
    # Test asyncpg connection
    asyncpg_success = await test_asyncpg_connection()
    
    # Test SQLAlchemy connection
    engine = test_sqlalchemy_connection()
    sqlalchemy_success = bool(engine)
    
    if sqlalchemy_success:
        # Validate tables
        tables_success = validate_tables(engine)
        
        # Test basic CRUD
        crud_success = test_basic_crud(engine)
    else:
        tables_success = False
        crud_success = False
    
    # Print summary
    logger.info("\n----- TEST SUMMARY -----")
    logger.info(f"AsyncPG Connection: {'✅ PASS' if asyncpg_success else '❌ FAIL'}")
    logger.info(f"SQLAlchemy Connection: {'✅ PASS' if sqlalchemy_success else '❌ FAIL'}")
    logger.info(f"Table Validation: {'✅ PASS' if tables_success else '❌ FAIL'}")
    logger.info(f"CRUD Operations: {'✅ PASS' if crud_success else '❌ FAIL'}")
    logger.info("-----------------------\n")
    
    if all([asyncpg_success, sqlalchemy_success, tables_success, crud_success]):
        logger.info("✅ All database tests passed successfully!")
        return 0
    else:
        logger.error("❌ Some database tests failed. See logs above for details.")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
