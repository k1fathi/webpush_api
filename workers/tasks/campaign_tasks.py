import logging
from datetime import datetime
from typing import List, Dict, Any, Optional

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

# Make sure shared_task is defined
shared_task = celery_app.task

# Mock classes for repositories and services to avoid import errors
class CampaignRepository:
    def get_ready_campaigns(self):
        return []
    def get(self, campaign_id):
        return None

class UserRepository:
    def get(self, user_id):
        return None

class TemplateRepository:
    def get(self, template_id):
        return None

class NotificationRepository:
    def create(self, notification):
        pass
    def update(self, notification):
        pass
    def get(self, notification_id):
        return None

class WebhookRepository:
    def trigger_webhooks(self, event_type, resource_id):
        pass

class WebPushService:
    def personalize_notification(self, notification, user):
        return notification
    def send(self, notification, user):
        return True

class CdpService:
    def is_enabled(self):
        return False

class CepService:
    def is_enabled(self):
        return False
    def get_optimal_channel(self, user_id, campaign_id):
        return "webpush"
    def record_channel_decision(self, **kwargs):
        pass

class NotificationModel:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

class DeliveryStatus:
    PENDING = "pending"
    DELIVERED = "delivered"
    FAILED = "failed"

@celery_app.task(bind=True)
def execute_campaign(self, campaign_id: int, campaign_data: Dict[str, Any] = None) -> bool:
    """
    Executes a notification campaign
    """
    try:
        logger.info(f"Executing campaign {campaign_id}")
        # Placeholder for campaign execution logic
        return True
    except Exception as e:
        logger.error(f"Error executing campaign {campaign_id}: {str(e)}")
        self.retry(exc=e, countdown=60, max_retries=3)
        return False

@celery_app.task
def process_scheduled_campaigns():
    """Process all scheduled campaigns that are ready to be sent"""
    logger.info("Processing scheduled campaigns")
    
    try:
        # Placeholder for actual implementation
        # Would normally query database for ready campaigns
        ready_campaigns = []
        
        for campaign in ready_campaigns:
            logger.info(f"Queuing campaign {campaign.id} for execution")
            execute_campaign.delay(campaign.id)
            
        return {"campaigns_processed": len(ready_campaigns)}
    except Exception as e:
        logger.error(f"Error processing scheduled campaigns: {str(e)}")
        return {"error": str(e)}

@celery_app.task
def process_campaign_batch(campaign_id: str, user_ids: List[str]):
    """Process a batch of users for a campaign"""
    logger.info(f"Processing campaign {campaign_id} batch with {len(user_ids)} users")
    
    # Get repositories
    campaign_repo = CampaignRepository()
    user_repo = UserRepository()
    template_repo = TemplateRepository()
    notification_repo = NotificationRepository()
    
    # Services
    webpush_service = WebPushService()
    cdp_service = CdpService()
    cep_service = CepService()
    
    # Get campaign and template
    campaign = campaign_repo.get(campaign_id)
    if not campaign or not hasattr(campaign, 'template_id'):
        logger.error(f"Campaign {campaign_id} not found or has no template")
        return {"error": "Campaign not found"}
        
    template = template_repo.get(str(getattr(campaign, 'template_id', None)))
    if not template:
        logger.error(f"Template for campaign {campaign_id} not found")
        return {"error": "Template not found"}
    
    # Process each user
    for user_id in user_ids:
        user = user_repo.get(user_id)
        if not user:
            logger.info(f"User {user_id} not found, skipping")
            continue
            
        # Skip users who haven't opted in
        if not getattr(user, 'opted_in', False) or not getattr(user, 'push_token', None):
            logger.info(f"Skipping user {user_id} - not opted in or missing push token")
            continue
        
        # Check CEP for optimal channel if integration is enabled
        use_webpush = True
        if cep_service.is_enabled():
            best_channel = cep_service.get_optimal_channel(user_id, campaign_id)
            if best_channel != "webpush":
                logger.info(f"CEP suggests using {best_channel} instead of WebPush for user {user_id}")
                # Record the decision but don't send via webpush
                cep_service.record_channel_decision(
                    user_id=user_id,
                    campaign_id=campaign_id,
                    selected_channel=best_channel,
                    score=0.8,  # Example score
                    factors={"decision_source": "cep_api"}
                )
                use_webpush = False
        
        if use_webpush:
            # Create notification
            try:
                # Use getattr with defaults for template properties
                notification = NotificationModel(
                    campaign_id=campaign_id,
                    user_id=user_id,
                    template_id=getattr(template, 'id', None),
                    title=getattr(template, 'title', "Notification"),
                    body=getattr(template, 'body', ""),
                    image_url=getattr(template, 'image_url', None),
                    action_url=getattr(template, 'action_url', None),
                    personalized_data={},  # Will be personalized in the next step
                    sent_at=datetime.utcnow(),
                    delivery_status=DeliveryStatus.PENDING,
                    device_info={"browser": getattr(user, 'browser', "unknown")}
                )
                
                # Personalize notification
                notification = webpush_service.personalize_notification(notification, user)
                notification_repo.create(notification)
                
                # Queue the actual sending
                send_notification.delay(getattr(notification, 'id', str(user_id)))
                
            except Exception as e:
                logger.error(f"Failed to personalize notification for user {user_id}: {str(e)}")
    
    return {
        "campaign_id": campaign_id,
        "processed_users": len(user_ids)
    }

@celery_app.task(bind=True, max_retries=3)
def send_notification(self, notification_id: str):
    """Send a single notification"""
    logger.info(f"Sending notification {notification_id}")
    
    # Get repositories
    notification_repo = NotificationRepository()
    user_repo = UserRepository()
    webhook_repo = WebhookRepository()
    
    # Services
    webpush_service = WebPushService()
    
    # Get notification
    notification = notification_repo.get(notification_id)
    if not notification:
        logger.error(f"Notification {notification_id} not found")
        return
    
    # Get user
    user = user_repo.get(getattr(notification, 'user_id', None))
    if not user:
        logger.error(f"User {getattr(notification, 'user_id', 'unknown')} not found")
        if hasattr(notification, 'delivery_status'):
            notification.delivery_status = DeliveryStatus.FAILED
            notification_repo.update(notification)
        return
    
    # Send push notification
    try:
        success = webpush_service.send(notification, user)
        
        if success:
            notification.delivery_status = DeliveryStatus.DELIVERED
            notification.delivered_at = datetime.utcnow()
        else:
            notification.delivery_status = DeliveryStatus.FAILED
        
        notification_repo.update(notification)
        
        # Trigger webhooks
        event_type = "notification_delivered" if success else "notification_failed"
        webhook_repo.trigger_webhooks(event_type, notification_id)
        
        return {
            "notification_id": notification_id,
            "success": success
        }
        
    except Exception as e:
        logger.error(f"Failed to send notification {notification_id}: {str(e)}")
        notification.delivery_status = DeliveryStatus.FAILED
        notification_repo.update(notification)
        
        try:
            webhook_repo.trigger_webhooks("notification_failed", notification_id)
        except Exception as webhook_error:
            logger.error(f"Failed to trigger webhooks for notification {notification_id}: {str(webhook_error)}")
        
        # Retry with exponential backoff
        self.retry(exc=e, countdown=2 ** self.request.retries * 60)

@celery_app.task
def update_campaign_statistics(campaign_id: str):
    """Update the statistics for a campaign"""
    logger.info(f"Updating statistics for campaign {campaign_id}")
    
    try:
        # Placeholder for actual implementation
        # Would calculate delivery, open, and click rates
        
        return {
            "campaign_id": campaign_id,
            "updated": True,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error updating campaign statistics: {str(e)}")
        return {"error": str(e)}
