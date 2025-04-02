import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from core.celery_app import celery_app
from core.config import settings
from models.analytics import Analytics
from models.domain.notification import DeliveryStatus
from repositories.analytics import AnalyticsRepository
from repositories.campaign import CampaignRepository
from repositories.notification import NotificationRepository
from repositories.user import UserRepository
from repositories.webhook import WebhookRepository
from services.cdp import CdpService

logger = logging.getLogger(__name__)

@celery_app.task
def process_analytics_event(analytics_id: str, event_type: str):
    """Process an analytics event"""
    logger.info(f"Processing analytics event {analytics_id} of type {event_type}")
    
    # Get repositories
    analytics_repo = AnalyticsRepository()
    webhook_repo = WebhookRepository()
    
    # Process based on event type
    if event_type == "send":
        # Nothing special to do for send events
        pass
    
    elif event_type == "delivery":
        # Nothing special to do for delivery events
        pass
    
    elif event_type == "open":
        # Trigger webhooks for open events
        analytics = analytics_repo.get(analytics_id)
        if analytics:
            webhook_repo.trigger_webhooks("notification_opened", analytics.notification_id)
    
    elif event_type == "click":
        # Trigger webhooks for click events
        analytics = analytics_repo.get(analytics_id)
        if analytics:
            webhook_repo.trigger_webhooks("notification_clicked", analytics.notification_id)
            
            # Schedule conversion tracking task
            monitor_for_conversion.delay(analytics.notification_id)
    
    elif event_type == "conversion":
        # Trigger webhooks for conversion events
        analytics = analytics_repo.get(analytics_id)
        if analytics:
            webhook_repo.trigger_webhooks("notification_converted", analytics.notification_id)
    
    elif event_type == "failure":
        # Nothing special to do for failure events
        pass
        
    # Sync with CDP if enabled
    if settings.CDP_API_URL:
        sync_analytics_with_cdp.delay(analytics_id)

@celery_app.task
def monitor_for_conversion(notification_id: str, timeout_hours: int = 24):
    """
    Monitor for conversions from a notification
    This task would check if a conversion event has occurred within a timeframe
    """
    logger.info(f"Monitoring for conversions from notification {notification_id}")
    
    # Get repositories
    notification_repo = NotificationRepository()
    analytics_repo = AnalyticsRepository()
    
    # Check if notification exists
    notification = notification_repo.get(notification_id)
    if not notification:
        logger.error(f"Notification {notification_id} not found")
        return
        
    # Check if notification was clicked (prerequisite for conversion)
    if notification.clicked_at:
        # In a real implementation, this would check external systems (e.g., e-commerce platform)
        # or wait for a conversion callback. For this example, we just log.
        logger.info(f"Waiting for conversion data for notification {notification_id}")
        
        # Re-schedule this task to check again later if within timeout period
        click_time = notification.clicked_at
        current_time = datetime.now()
        hours_since_click = (current_time - click_time).total_seconds() / 3600
        
        if hours_since_click < timeout_hours:
            # Check again in 1 hour
            monitor_for_conversion.apply_async(
                args=[notification_id, timeout_hours],
                countdown=3600  # 1 hour
            )
        else:
            logger.info(f"Conversion monitoring timeout for notification {notification_id}")
            
            # Record the final analytics
            calculate_campaign_statistics.delay(str(notification.campaign_id))

@celery_app.task
def sync_analytics_with_cdp(analytics_id: str):
    """Sync analytics data with Customer Data Platform"""
    logger.info(f"Syncing analytics data {analytics_id} with CDP")
    
    # Get repositories
    analytics_repo = AnalyticsRepository()
    user_repo = UserRepository()
    notification_repo = NotificationRepository()
    
    # Get CDP service
    cdp_service = CdpService()
    
    # Check if CDP integration is enabled
    if not cdp_service.is_enabled():
        logger.info("CDP integration not enabled, skipping sync")
        return
        
    # Get the analytics event
    analytics = analytics_repo.get(analytics_id)
    if not analytics:
        logger.error(f"Analytics event {analytics_id} not found")
        return
        
    # Get user and notification data
    user = user_repo.get(analytics.user_id)
    notification = notification_repo.get(analytics.notification_id)
    
    if not user or not notification:
        logger.error(f"Missing user or notification data for analytics event {analytics_id}")
        return
        
    # Prepare data for CDP
    cdp_data = {
        "user_id": str(analytics.user_id),
        "event_type": analytics.user_action,
        "timestamp": analytics.event_time.isoformat(),
        "properties": {
            "notification_id": str(analytics.notification_id),
            "campaign_id": str(analytics.campaign_id),
            "delivered": analytics.delivered,
            "opened": analytics.opened,
            "clicked": analytics.clicked,
        }
    }
    
    if analytics.conversion_type:
        cdp_data["properties"]["conversion_type"] = analytics.conversion_type.value
        cdp_data["properties"]["conversion_value"] = analytics.conversion_value
        
    # Send to CDP
    try:
        success = cdp_service.track_event(cdp_data)
        if success:
            logger.info(f"Successfully synced analytics event {analytics_id} with CDP")
        else:
            logger.error(f"Failed to sync analytics event {analytics_id} with CDP")
            
            # Retry with exponential backoff
            sync_analytics_with_cdp.apply_async(
                args=[analytics_id],
                countdown=60 * 5  # 5 minutes
            )
    except Exception as e:
        logger.error(f"Error syncing analytics event {analytics_id} with CDP: {str(e)}")
        
        # Retry with exponential backoff
        sync_analytics_with_cdp.apply_async(
            args=[analytics_id],
            countdown=60 * 5  # 5 minutes
        )

@celery_app.task
def calculate_campaign_statistics(campaign_id: str):
    """Calculate and update statistics for a campaign"""
    logger.info(f"Calculating statistics for campaign {campaign_id}")
    
    # Get repositories
    campaign_repo = CampaignRepository()
    analytics_repo = AnalyticsRepository()
    notification_repo = NotificationRepository()
    
    # Get campaign
    campaign = campaign_repo.get(campaign_id)
    if not campaign:
        logger.error(f"Campaign {campaign_id} not found")
        return
        
    # Calculate statistics
    total_sent = notification_repo.count_by_campaign(campaign_id)
    total_delivered = analytics_repo.count_delivered_by_campaign(campaign_id)
    total_opened = analytics_repo.count_opened_by_campaign(campaign_id)
    total_clicked = analytics_repo.count_clicked_by_campaign(campaign_id)
    
    # Calculate rates
    delivery_rate = total_delivered / total_sent if total_sent > 0 else 0
    open_rate = total_opened / total_delivered if total_delivered > 0 else 0
    click_rate = total_clicked / total_opened if total_opened > 0 else 0
    
    # Get conversions
    conversions = analytics_repo.get_conversions_for_campaign(campaign_id)
    total_conversions = len(conversions)
    conversion_rate = total_conversions / total_clicked if total_clicked > 0 else 0
    
    # Update campaign statistics (if your campaign model has these fields)
    # This would depend on your specific campaign model implementation
    # campaign.stats = {
    #     "sent": total_sent,
    #     "delivered": total_delivered,
    #     "opened": total_opened,
    #     "clicked": total_clicked,
    #     "conversions": total_conversions,
    #     "delivery_rate": delivery_rate,
    #     "open_rate": open_rate,
    #     "click_rate": click_rate,
    #     "conversion_rate": conversion_rate,
    #     "last_updated": datetime.now().isoformat()
    # }
    # campaign_repo.update(campaign)
    
    logger.info(f"Campaign {campaign_id} statistics calculated: "
                f"Sent={total_sent}, Delivered={total_delivered}, Opened={total_opened}, "
                f"Clicked={total_clicked}, Conversions={total_conversions}")
    
    # Trigger webhook for campaign statistics update
    webhook_repo = WebhookRepository()
    webhook_repo.trigger_webhooks("campaign_stats_updated", campaign_id)

@celery_app.task
def cleanup_old_analytics():
    """Clean up old analytics data based on retention policy"""
    logger.info("Cleaning up old analytics data")
    
    # This would implement your data retention policy
    # For example, removing analytics data older than X months
    # Or aggregating old data into summary statistics
    
    # Implementation would depend on your specific requirements
    pass
