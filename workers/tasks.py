from celery import shared_task
from workers.celery_worker import celery_app
from core.database import SessionLocal
from core.models import Notification, Subscription
from sqlalchemy import exc
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

@celery_app.task(
    name='tasks.process_notification',
    bind=True,
    max_retries=3,
    default_retry_delay=60,
    acks_late=True
)
def process_notification(self, notification_id: int):
    """
    Process and send notification to all active subscriptions
    """
    logger.info(f"Processing notification {notification_id}")
    db = SessionLocal()
    
    try:
        # Get notification
        notification = db.query(Notification).filter(Notification.id == notification_id).first()
        if not notification:
            logger.error(f"Notification {notification_id} not found")
            return {"status": "error", "message": "Notification not found"}

        # Get all active subscriptions
        subscriptions = db.query(Subscription).all()
        
        successful_pushes = 0
        failed_pushes = 0

        for subscription in subscriptions:
            try:
                # Here you would implement the actual web push sending logic
                # using pywebpush or a similar library
                
                # Update last push timestamp
                subscription.last_push_at = datetime.utcnow()
                successful_pushes += 1
                
            except Exception as push_error:
                logger.error(f"Failed to push to subscription {subscription.id}: {str(push_error)}")
                failed_pushes += 1

        db.commit()
        
        return {
            "status": "success",
            "notification_id": notification_id,
            "successful_pushes": successful_pushes,
            "failed_pushes": failed_pushes
        }

    except exc.SQLAlchemyError as db_error:
        logger.error(f"Database error while processing notification {notification_id}: {str(db_error)}")
        db.rollback()
        raise self.retry(exc=db_error)
        
    except Exception as e:
        logger.error(f"Unexpected error processing notification {notification_id}: {str(e)}")
        raise
        
    finally:
        db.close()

@celery_app.task(name='tasks.cleanup_old_notifications')
def cleanup_old_notifications(days: int = 30):
    """
    Clean up notifications older than specified days
    """
    db = SessionLocal()
    try:
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        db.query(Notification).filter(Notification.created_at < cutoff_date).delete()
        db.commit()
        return {"status": "success", "message": f"Cleaned up notifications older than {days} days"}
    except Exception as e:
        logger.error(f"Failed to cleanup old notifications: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()
