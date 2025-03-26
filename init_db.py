from database import engine, Base
import logging

logger = logging.getLogger(__name__)

def init_database():
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Database tables created successfully")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to create database tables: {str(e)}")
        return False

if __name__ == "__main__":
    init_database()
