from celery import shared_task
from workers.celery_worker import celery_app
from db.databse_manager import SessionLocal
from db.models import (
    Notification, WebhookEvent, DeliveryStatus
)
from core.models import Subscription
from sqlalchemy import exc
from datetime import datetime, timedelta
import logging
import httpx

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

@shared_task(bind=True, max_retries=3)
def process_webhook_event(self, event_id: int):
    """Process webhook event and send to external systems"""
    db = SessionLocal()
    try:
        event = db.query(WebhookEvent).filter(WebhookEvent.id == event_id).first()
        if not event:
            logger.error(f"Webhook event {event_id} not found")
            return False

        # Send webhook to external system using synchronous client
        with httpx.Client() as client:
            webhook_data = {
                "notification_id": event.notification_id,
                "subscription_id": event.subscription_id,
                "timestamp": event.created_at.isoformat(),
                **event.payload
            }

            if event.event_type == "delivery":
                webhook_data["event"] = "delivery"
                response = client.post(
                    event.payload.get("webhook_url"),
                    json=webhook_data
                )
            elif event.event_type == "click":
                webhook_data["event"] = "click"
                response = client.post(
                    event.payload.get("webhook_url"),
                    json=webhook_data
                )
            
            response.raise_for_status()

        event.processed = True
        db.commit()
        return True

    except httpx.HTTPError as http_error:
        logger.error(f"HTTP error while processing webhook event {event_id}: {str(http_error)}")
        db.rollback()
        raise self.retry(exc=http_error, countdown=5 * (self.request.retries + 1))
    except Exception as e:
        logger.error(f"Error processing webhook event {event_id}: {str(e)}")
        db.rollback()
        raise self.retry(exc=e, countdown=5 * (self.request.retries + 1))
    finally:
        db.close()
