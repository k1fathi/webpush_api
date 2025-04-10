#!/usr/bin/env python
"""
Simple database connection test script

This script confirms connection to the database using both direct psycopg2
and SQLAlchemy connections with the current environment settings.
"""

import os
import sys
import logging
from pathlib import Path

# Add the project root to Python path
sys.path.append(str(Path(__file__).parent.parent))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_direct_psycopg2_connection():
    """Test direct connection with psycopg2"""
    try:
        import psycopg2
        from core.config import settings

        logger.info("Testing direct PostgreSQL connection with psycopg2...")
        
        # Create connection string
        conn_params = {
            'host': settings.POSTGRES_SERVER,
            'port': settings.POSTGRES_PORT,
            'user': settings.POSTGRES_USER,
            'password': settings.POSTGRES_PASSWORD,
            'dbname': settings.POSTGRES_DB
        }
        
        # Log connection info (masked)
        conn_info = conn_params.copy()
        conn_info['password'] = '********'
        logger.info(f"Connection parameters: {conn_info}")
        
        # Try to connect
        conn = psycopg2.connect(**conn_params)
        
        # Check connection
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        logger.info(f"Connection successful! PostgreSQL version: {version}")
        
        # Get list of databases
        cursor.execute("SELECT datname FROM pg_database;")
        databases = [row[0] for row in cursor.fetchall()]
        logger.info(f"Available databases: {', '.join(databases)}")
        
        # Close connection
        cursor.close()
        conn.close()
        
        return True
    except ImportError:
        logger.error("psycopg2 is not installed. Run: pip install psycopg2-binary")
        return False
    except Exception as e:
        logger.error(f"Connection failed: {str(e)}")
        return False

def test_sqlalchemy_connection():
    """Test connection with SQLAlchemy"""
    try:
        from sqlalchemy import create_engine, text
        from core.config import settings
        
        logger.info("Testing SQLAlchemy connection...")
        
        # Get database URI from settings
        db_uri = settings.SQLALCHEMY_DATABASE_URI
        masked_uri = str(db_uri).replace(settings.POSTGRES_PASSWORD, '********')
        logger.info(f"Using database URI: {masked_uri}")
        
        # Create engine
        engine = create_engine(str(db_uri).replace('+asyncpg', ''))
        
        # Try to connect
        with engine.connect() as connection:
            result = connection.execute(text("SELECT version();"))
            version = result.scalar()
            logger.info(f"SQLAlchemy connection successful! PostgreSQL version: {version}")
            
            # Get list of tables
            result = connection.execute(text(
                "SELECT table_name FROM information_schema.tables "
                "WHERE table_schema = 'public';"
            ))
            tables = [row[0] for row in result]
            if tables:
                logger.info(f"Tables in database: {', '.join(tables)}")
            else:
                logger.info("No tables found in database.")
                
        return True
    except ImportError:
        logger.error("SQLAlchemy is not installed. Run: pip install sqlalchemy")
        return False
    except Exception as e:
        logger.error(f"SQLAlchemy connection failed: {str(e)}")
        return False

if __name__ == "__main__":
    print("\n=== DATABASE CONNECTION TEST ===\n")
    
    # Run direct connection test
    direct_conn_success = test_direct_psycopg2_connection()
    
    print("\n" + "-" * 50 + "\n")
    
    # Run SQLAlchemy connection test
    sqlalchemy_conn_success = test_sqlalchemy_connection()
    
    print("\n" + "=" * 50)
    print("\nCONNECTION TEST SUMMARY:")
    print(f"Direct Connection: {'✅ SUCCESS' if direct_conn_success else '❌ FAILED'}")
    print(f"SQLAlchemy Connection: {'✅ SUCCESS' if sqlalchemy_conn_success else '❌ FAILED'}")
    print("=" * 50 + "\n")
    
    # Exit with status code
    sys.exit(0 if direct_conn_success and sqlalchemy_conn_success else 1)
