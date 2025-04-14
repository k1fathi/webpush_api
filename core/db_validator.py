import logging
import time
from typing import List, Tuple, Optional
from sqlalchemy import inspect, text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError, OperationalError

from core.config import settings

logger = logging.getLogger(__name__)

def test_database_connection(engine: Engine) -> Tuple[bool, Optional[str]]:
    """
    Test the database connection
    
    Args:
        engine: SQLAlchemy engine
    
    Returns:
        Tuple of (success, error_message)
    """
    retry_attempts = settings.DB_RETRY_ATTEMPTS
    retry_delay = settings.DB_RETRY_DELAY
    
    for attempt in range(1, retry_attempts + 1):
        try:
            # Simple connection test with timeout
            with engine.connect() as connection:
                connection.execute(text("SELECT 1")).fetchone()
            logger.info("Database connection successful")
            return True, None
        except OperationalError as e:
            logger.warning(f"Database connection failed (attempt {attempt}/{retry_attempts}): {str(e)}")
            if attempt < retry_attempts:
                logger.info(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                error_msg = f"Failed to connect to database after {retry_attempts} attempts: {str(e)}"
                logger.error(error_msg)
                return False, error_msg
        except SQLAlchemyError as e:
            error_msg = f"Database error: {str(e)}"
            logger.error(error_msg)
            return False, error_msg
    
    return False, "Unknown database connection error"

def validate_tables(engine: Engine, required_tables: List[str]) -> Tuple[bool, Optional[str]]:
    """
    Validate that all required tables exist in the database
    
    Args:
        engine: SQLAlchemy engine
        required_tables: List of table names that must exist
    
    Returns:
        Tuple of (success, error_message)
    """
    try:
        inspector = inspect(engine)
        existing_tables = inspector.get_table_names()
        
        # Convert to lowercase for case-insensitive comparison
        existing_tables_lower = [table.lower() for table in existing_tables]
        missing_tables = [table for table in required_tables if table.lower() not in existing_tables_lower]
        
        if missing_tables:
            error_msg = f"Missing required tables: {', '.join(missing_tables)}"
            logger.error(error_msg)
            return False, error_msg
        
        logger.info(f"All required tables exist: {', '.join(required_tables)}")
        return True, None
    except SQLAlchemyError as e:
        error_msg = f"Error validating tables: {str(e)}"
        logger.error(error_msg)
        return False, error_msg

async def validate_database(engine: Engine) -> Tuple[bool, Optional[str]]:
    """
    Comprehensive database validation that can be called during application startup
    
    Args:
        engine: SQLAlchemy engine
    
    Returns:
        Tuple of (success, error_message)
    """
    # Check connection
    conn_success, conn_error = test_database_connection(engine)
    if not conn_success:
        return False, conn_error
    
    # Check tables
    if settings.REQUIRED_TABLES:
        tables_success, tables_error = validate_tables(engine, settings.REQUIRED_TABLES)
        if not tables_success:
            return False, tables_error
    
    return True, None
