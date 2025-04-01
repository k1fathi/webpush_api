import logging
from datetime import datetime
from typing import List

from core.celery_app import celery_app
from models.domain.campaign import CampaignModel, CampaignStatus
from models.domain.notification import DeliveryStatus, NotificationModel
from repositories.campaign import CampaignRepository
from repositories.notification import NotificationRepository
from repositories.segment import SegmentRepository
from repositories.template import TemplateRepository
from repositories.user import UserRepository
from repositories.webhook import WebhookRepository
from services.cdp import CdpService
from services.cep import CepService
from services.webpush import WebPushService

logger = logging.getLogger(__name__)

@celery_app.task
def process_scheduled_campaigns():
    """Process all scheduled campaigns that are ready to be sent"""
    logger.info("Processing scheduled campaigns")
    campaign_repo = CampaignRepository()
    
    # Get campaigns that are scheduled to run now
    ready_campaigns = campaign_repo.get_ready_campaigns()
    
    for campaign in ready_campaigns:
        logger.info(f"Queuing campaign {campaign.id} - {campaign.name} for execution")
        execute_campaign.delay(str(campaign.id))

@celery_app.task
def execute_campaign(campaign_id: str):
    """Execute a specific campaign"""
    logger.info(f"Executing campaign {campaign_id}")
    
    # Get repositories
    campaign_repo = CampaignRepository()
    segment_repo = SegmentRepository()
    template_repo = TemplateRepository()
    user_repo = UserRepository()
    notification_repo = NotificationRepository()
    webhook_repo = WebhookRepository()
    
    # Services
    webpush_service = WebPushService()
    cdp_service = CdpService()
    cep_service = CepService()
    
    # Get campaign
    campaign = campaign_repo.get(campaign_id)
    if not campaign:
        logger.error(f"Campaign {campaign_id} not found")
        return
    
    # Update campaign status
    campaign.status = CampaignStatus.RUNNING
    campaign_repo.update(campaign)
    
    # Get segment users
    segment = segment_repo.get(str(campaign.segment_id))
    if not segment:
        logger.error(f"Segment {campaign.segment_id} not found")
        campaign.status = CampaignStatus.CANCELLED
        campaign_repo.update(campaign)
        return
    
    # Get template
    template = template_repo.get(str(campaign.template_id))
    if not template:
        logger.error(f"Template {campaign.template_id} not found")
        campaign.status = CampaignStatus.CANCELLED
        campaign_repo.update(campaign)
        return
    
    # Get users in segment
    users = segment_repo.get_users(str(segment.id))
    
    # Process each user in batches
    batch_size = 100
    for i in range(0, len(users), batch_size):
        user_batch = users[i:i + batch_size]
        process_campaign_batch.delay(campaign_id, [str(user.id) for user in user_batch])
    
    logger.info(f"Campaign {campaign_id} queued for sending to {len(users)} users")

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

@celery_app.task(max_retries=3)
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
    
    # Add implementation here
    pass
