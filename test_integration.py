import asyncio
import logging
from fastapi.testclient import TestClient
from main import app
from database import SessionLocal
from models import Notification
from celery_worker import celery_app
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

client = TestClient(app)

def test_database_connection():
    """Test PostgreSQL connection and basic operations"""
    try:
        db = SessionLocal()
        # Try to execute a simple query
        result = db.execute("SELECT 1").fetchone()
        logger.info("✅ Database connection successful")
        return True
    except Exception as e:
        logger.error(f"❌ Database connection failed: {str(e)}")
        return False
    finally:
        db.close()

def test_rabbitmq_connection():
    """Test RabbitMQ connection"""
    try:
        # Try to connect to RabbitMQ
        celery_app.connection().ensure_connection(timeout=3)
        logger.info("✅ RabbitMQ connection successful")
        return True
    except Exception as e:
        logger.error(f"❌ RabbitMQ connection failed: {str(e)}")
        return False

def test_celery_task():
    """Test Celery task execution"""
    db = None
    try:
        # First ensure tables exist
        from init_db import init_database
        init_database()
        
        # Create a test notification
        response = client.post(
            "/notifications/",
            json={
                "template": {"title": "Test", "body": "Test notification"},
                "segments": ["test_segment"],
                "metadata": {"test": True}
            }
        )
        
        if response.status_code != 200:
            logger.error(f"❌ Failed to create notification: {response.text}")
            return False

        notification_id = response.json()["id"]
        
        # Wait for task processing
        time.sleep(2)
        
        # Check if notification was processed
        db = SessionLocal()
        notification = db.query(Notification).filter(Notification.id == notification_id).first()
        
        if notification:
            logger.info(f"✅ Celery task processed notification {notification_id}")
            return True
        else:
            logger.error("❌ Celery task failed to process notification")
            return False
            
    except Exception as e:
        logger.error(f"❌ Celery task test failed: {str(e)}")
        return False
    finally:
        if db is not None:
            db.close()

def run_all_tests():
    """Run all integration tests"""
    logger.info("🔍 Starting integration tests...")
    
    # Test database
    db_ok = test_database_connection()
    
    # Test RabbitMQ
    rabbitmq_ok = test_rabbitmq_connection()
    
    # Test Celery task
    celery_ok = test_celery_task()
    
    # Summary
    logger.info("\n=== Test Results ===")
    logger.info(f"Database: {'✅' if db_ok else '❌'}")
    logger.info(f"RabbitMQ: {'✅' if rabbitmq_ok else '❌'}")
    logger.info(f"Celery: {'✅' if celery_ok else '❌'}")
    
    return all([db_ok, rabbitmq_ok, celery_ok])

if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)
