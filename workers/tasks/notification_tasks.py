import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List

# Set up logger
logger = logging.getLogger(__name__)

# Import safely
try:
    from core.celery_app import celery_app
except ImportError:
    logger.warning("Could not import celery_app from core.celery_app")
    # Create a no-op decorator for development/testing
    def shared_task(*args, **kwargs):
        def decorator(func):
            return func
        return decorator
    celery_app = type('MockCelery', (), {'task': shared_task})

# Mock classes needed for safe imports
class DeliveryStatus:
    PENDING = "pending"
    DELIVERED = "delivered"
    FAILED = "failed"
    
class NotificationRepository:
    def get_pending_notifications(self, limit=100):
        return []
    
    def get(self, notification_id):
        return None

class NotificationService:
    def send_notification(self, notification_id):
        return True
    
    def create_notifications_for_campaign(self, campaign_id, user_batch):
        return []

class AnalyticsService:
    def record_delivery(self, notification_id):
        return True
    
    def record_open(self, notification_id):
        return True
    
    def record_click(self, notification_id):
        return True

# Basic task implementations
@celery_app.task(bind=True)
def send_notification(self, user_id: int, notification_data: Dict[str, Any] = None) -> bool:
    """
    Sends a push notification to a user
    """
    try:
        notification_data = notification_data or {"title": "Notification"}
        logger.info(f"Sending notification to user {user_id}: {notification_data.get('title', 'Untitled')}")
        # Placeholder for actual notification sending logic
        return True
    except Exception as e:
        logger.error(f"Error sending notification to user {user_id}: {str(e)}")
        self.retry(exc=e, countdown=30, max_retries=3)
        return False

@celery_app.task(bind=True)
def process_pending_notifications(self, batch_size: int = 100) -> Dict[str, Any]:
    """
    Processes pending notifications from the database
    """
    try:
        logger.info(f"Processing up to {batch_size} pending notifications")
        
        notification_repo = NotificationRepository()
        notification_service = NotificationService()
        
        # Get pending notifications
        pending_notifications = notification_repo.get_pending_notifications(limit=batch_size)
        
        if not pending_notifications:
            logger.info("No pending notifications found")
            return {"processed": 0}
            
        logger.info(f"Found {len(pending_notifications)} pending notifications")
        
        success_count = 0
        failure_count = 0
        
        # Process each notification
        for notification in pending_notifications:
            try:
                result = notification_service.send_notification(notification.id)
                if result:
                    success_count += 1
                else:
                    failure_count += 1
            except Exception as e:
                logger.error(f"Error processing notification {notification.id}: {str(e)}")
                failure_count += 1
        
        logger.info(f"Processed {success_count + failure_count} notifications: {success_count} succeeded, {failure_count} failed")
        return {
            "processed": success_count + failure_count,
            "success": success_count,
            "failure": failure_count
        }
    except Exception as e:
        logger.error(f"Error processing pending notifications: {str(e)}")
        self.retry(exc=e, countdown=60, max_retries=3)
        return {"processed": 0, "error": str(e)}

@celery_app.task
def track_notification_delivery(notification_id: str):
    """Track delivery of a notification in analytics"""
    logger.info(f"Tracking delivery of notification {notification_id}")
    
    analytics_service = AnalyticsService()
    
    try:
        # Record delivery event in analytics
        analytics_service.record_delivery(notification_id)
        
        # Update test variant metrics if this is part of an A/B test
        notification_repo = NotificationRepository()
        notification = notification_repo.get(notification_id)
        
        if notification and notification.variant_id:
            from tasks.ab_test_tasks import track_variant_engagement
            track_variant_engagement.delay(notification_id, "delivery")
            
        return True
    except Exception as e:
        logger.error(f"Error tracking notification delivery: {str(e)}")
        return False

@celery_app.task
def track_notification_open(notification_id: str):
    """Track open of a notification in analytics"""
    logger.info(f"Tracking open of notification {notification_id}")
    
    analytics_service = AnalyticsService()
    
    try:
        # Record open event in analytics
        analytics_service.record_open(notification_id)
        
        # Update test variant metrics if this is part of an A/B test
        notification_repo = NotificationRepository()
        notification = notification_repo.get(notification_id)
        
        if notification and notification.variant_id:
            from tasks.ab_test_tasks import track_variant_engagement
            track_variant_engagement.delay(notification_id, "open")
            
        return True
    except Exception as e:
        logger.error(f"Error tracking notification open: {str(e)}")
        return False

@celery_app.task
def track_notification_click(notification_id: str):
    """Track click of a notification in analytics"""
    logger.info(f"Tracking click of notification {notification_id}")
    
    analytics_service = AnalyticsService()
    
    try:
        # Record click event in analytics
        analytics_service.record_click(notification_id)
        
        # Update test variant metrics if this is part of an A/B test
        notification_repo = NotificationRepository()
        notification = notification_repo.get(notification_id)
        
        if notification and notification.variant_id:
            from tasks.ab_test_tasks import track_variant_engagement
            track_variant_engagement.delay(notification_id, "click")
            
        # Schedule monitoring for conversions
        monitor_for_conversion.delay(notification_id)
            
        return True
    except Exception as e:
        logger.error(f"Error tracking notification click: {str(e)}")
        return False

@celery_app.task
def monitor_for_conversion(notification_id: str, timeout_hours: int = 24):
    """Monitor for conversions after a notification click"""
    logger.info(f"Monitoring for conversions from notification {notification_id}")
    
    # This would check if a conversion has happened within a specified timeframe
    # For now, we'll just log that we're monitoring
    
    # In a real implementation, you would:
    # 1. Check your analytics/events system for conversion events attributed to this notification
    # 2. If found, record the conversion in analytics
    # 3. If not found and still within timeout period, reschedule this task for later
    
    # Placeholder implementation
    notification_repo = NotificationRepository()
    notification = notification_repo.get(notification_id)
    
    if not notification:
        logger.error(f"Notification {notification_id} not found")
        return
        
    # Check if clicked and within monitoring window
    if notification.clicked_at:
        hours_since_click = (datetime.now() - notification.clicked_at).total_seconds() / 3600
        
        if hours_since_click < timeout_hours:
            # Still within monitoring window, reschedule check
            logger.info(f"Still monitoring for conversions from notification {notification_id}")
            # Check again in 1 hour
            monitor_for_conversion.apply_async(
                args=[notification_id, timeout_hours],
                countdown=3600  # 1 hour
            )
        else:
            logger.info(f"Conversion monitoring timeout for notification {notification_id}")

@celery_app.task
def process_campaign_notifications(campaign_id: str, user_batch: List[str]):
    """Process notifications for a campaign batch"""
    logger.info(f"Processing notifications for campaign {campaign_id}, {len(user_batch)} users")
    
    notification_service = NotificationService()
    
    try:
        # Create notifications
        notifications = notification_service.create_notifications_for_campaign(
            campaign_id, user_batch
        )
        
        # Queue each notification for sending
        for notification in notifications:
            send_notification.delay(notification.id)
            
        return {
            "campaign_id": campaign_id,
            "notifications_created": len(notifications),
            "user_count": len(user_batch)
        }
    except Exception as e:
        logger.error(f"Error processing campaign notifications: {str(e)}")
        return {
            "campaign_id": campaign_id,
            "error": str(e),
            "user_count": len(user_batch)
        }

@celery_app.task
def send_notification(notification_id: str):
    """Send a single notification"""
    logger.info(f"Sending notification {notification_id}")
    
    notification_service = NotificationService()
    
    try:
        result = notification_service.send_notification(notification_id)
        return {
            "notification_id": notification_id,
            "success": result
        }
    except Exception as e:
        logger.error(f"Error sending notification {notification_id}: {str(e)}")
        return {
            "notification_id": notification_id,
            "success": False,
            "error": str(e)
        }
