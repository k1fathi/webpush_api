import logging
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from core.config import settings
from core.db_validator import validate_database

logger = logging.getLogger(__name__)

# Create SQLAlchemy engine
engine = create_engine(
    settings.SQLALCHEMY_DATABASE_URI,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
    pool_recycle=settings.DB_POOL_RECYCLE,
    echo=settings.DB_ECHO_LOG,
    pool_pre_ping=True,  # Helps detect disconnections
)

# Create session class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for models
Base = declarative_base()

async def init_db():
    """Initialize database connection and validate"""
    if settings.VALIDATE_DB_ON_STARTUP:
        logger.info("Validating database connection and tables...")
        success, error = await validate_database(engine)
        
        if not success:
            logger.error(f"Database validation failed: {error}")
            raise Exception(f"Database validation failed: {error}")
        
        logger.info("Database validation successful")
    else:
        logger.info("Database validation skipped (VALIDATE_DB_ON_STARTUP is False)")
    
    return engine

async def create_tables():
    """Create all tables defined in models"""
    logger.info("Creating missing database tables")
    
    # Import all models here to ensure they are registered with Base
    # This import is placed here to avoid circular imports
    try:
        # Import models containing SQLAlchemy models
        # Adjust these imports to match your actual model modules
        from models.domain.user import UserModel
        from models.domain.subscription import SubscriptionModel
        from models.domain.notification import NotificationModel
        
        logger.info("Creating all defined tables...")
        Base.metadata.create_all(bind=engine)
        logger.info("Tables created successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to create tables: {e}")
        raise

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()