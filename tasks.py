from celery_worker import celery_app
from database import SessionLocal
from models import Notification
import logging

logger = logging.getLogger(__name__)

@celery_app.task(name='tasks.process_notification')
def process_notification(notification_id: int):
    logger.info(f"Processing notification {notification_id}")
    db = SessionLocal()
    try:
        notification = db.query(Notification).filter(Notification.id == notification_id).first()
        if notification:
            # Add your notification processing logic here
            logger.info(f"Successfully processed notification {notification_id}")
            return {"status": "success", "notification_id": notification_id}
        logger.error(f"Notification {notification_id} not found")
        return {"status": "error", "message": "Notification not found"}
    except Exception as e:
        logger.error(f"Error processing notification {notification_id}: {str(e)}")
        raise
    finally:
        db.close()
