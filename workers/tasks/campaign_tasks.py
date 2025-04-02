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

@shared_task
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
    template = template_repo.get(str(campaign.template_id))
    
    # Process each user
    for user_id in user_ids:
        user = user_repo.get(user_id)
        
        # Skip users who haven't opted in
        if not user.opted_in or not user.push_token:
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
            notification = NotificationModel(
                campaign_id=campaign.id,
                user_id=user.id,
                template_id=template.id,
                title=template.title,
                body=template.body,
                image_url=template.image_url,
                action_url=template.action_url,
                personalized_data={},  # Will be personalized in the next step
                sent_at=datetime.utcnow(),
                delivery_status=DeliveryStatus.PENDING,
                device_info={"browser": user.browser}
            )
            
            # Personalize notification
            try:
                notification = webpush_service.personalize_notification(notification, user)
                notification_repo.create(notification)
                
                # Queue the actual sending
                send_notification.delay(str(notification.id))
                
            except Exception as e:
                logger.error(f"Failed to personalize notification for user {user_id}: {str(e)}")

@shared_task(max_retries=3)
def send_notification(notification_id: str):
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
    user = user_repo.get(str(notification.user_id))
    if not user:
        logger.error(f"User {notification.user_id} not found")
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
        webhook_repo.trigger_webhooks(event_type, notification.id)
        
    except Exception as e:
        logger.error(f"Failed to send notification {notification_id}: {str(e)}")
        notification.delivery_status = DeliveryStatus.FAILED
        notification_repo.update(notification)
        
        try:
            webhook_repo.trigger_webhooks("notification_failed", notification.id)
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
            "timestamp": "2023-01-01T00:00:00Z"
        }
    except Exception as e:
        logger.error(f"Error updating campaign statistics: {str(e)}")
        return {"error": str(e)}
