from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config.settings import settings
import logging
import time
from sqlalchemy.exc import OperationalError
from sqlalchemy import inspect

logger = logging.getLogger(__name__)

def create_db_engine(max_retries=5, retry_delay=5):
    for attempt in range(max_retries):
        try:
            engine = create_engine(
                settings.DATABASE_URL,
                pool_size=5,
                max_overflow=10,
                pool_timeout=30,
                pool_recycle=1800
            )
            # Test the connection
            engine.connect()
            return engine
        except OperationalError as e:
            if attempt < max_retries - 1:
                logger.warning(f"Database connection attempt {attempt + 1} failed, retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                logger.error("Failed to connect to database after maximum retries")
                raise e

# Create engine with retry logic
engine = create_db_engine()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    try:
        # Import models here to ensure they are registered with Base
        from core.models import Notification, Subscription
        
        logger.info("Testing database connection...")
        with engine.connect() as conn:
            # Test connection
            conn.execute("SELECT 1")
            logger.info("Database connection successful")
            
            # Check if tables exist
            inspector = inspect(engine)
            existing_tables = inspector.get_table_names()
            logger.info(f"Existing tables: {existing_tables}")
            
            if "notifications" not in existing_tables:
                logger.info("Creating database tables...")
                Base.metadata.create_all(bind=engine)
                logger.info("✅ Database tables created successfully")
            else:
                logger.info("✅ Tables already exist")
                
        return True
    except Exception as e:
        logger.error(f"❌ Failed to initialize database: {str(e)}")
        raise

if __name__ == "__main__":
    init_db()
