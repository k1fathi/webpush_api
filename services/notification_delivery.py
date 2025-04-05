import logging
import uuid
import json  # Add missing import for json
from datetime import datetime
from typing import Dict, List, Optional, Any

# Optional import for pywebpush with fallback
try:
    from pywebpush import webpush, WebPushException
except ImportError:
    webpush = None
    WebPushException = Exception
    logging.warning("pywebpush module not found. Web push notifications will not work properly.")

from fastapi.encoders import jsonable_encoder

from core.config import settings
from models.schemas.notification import (
    Notification, NotificationCreate, NotificationRead, DeliveryStatus, NotificationType
)
from models.schemas.webpush import WebPushNotification
from repositories.notification import NotificationRepository
from repositories.user import UserRepository
from utils.audit import audit_log

logger = logging.getLogger(__name__)

class NotificationDeliveryService:
    """Service for delivering notifications to users"""
    
    def __init__(self, notification_repo: NotificationRepository):
        self.repo = notification_repo
        self.user_repo = UserRepository()
        self.vapid_claims = {
            'sub': f'mailto:{settings.VAPID_CLAIM_EMAIL}'
        }
    
    async def queue_notification(self, notification_create: NotificationCreate) -> str:
        """
        Queue a notification for delivery
        
        Args:
            notification_create: Notification data
            
        Returns:
            str: ID of the created notification
        """
        notification = Notification(
            id=str(uuid.uuid4()),
            campaign_id=notification_create.campaign_id,
            user_id=notification_create.user_id,
            template_id=notification_create.template_id,
            title=notification_create.title,
            body=notification_create.body,
            image_url=notification_create.image_url,
            action_url=notification_create.action_url,
            variant_id=notification_create.variant_id,
            personalized_data=notification_create.personalized_data or {},
            delivery_status=DeliveryStatus.QUEUED,
            device_info={},
            notification_type=notification_create.notification_type
        )
        
        created = await self.repo.create(notification)
        logger.info(f"Notification queued: {created.id}")
        return created.id
    
    async def queue_notifications_batch(self, notifications: List[NotificationCreate]) -> List[str]:
        """
        Queue multiple notifications for delivery in batch
        
        Args:
            notifications: List of notification data
            
        Returns:
            List[str]: IDs of the created notifications
        """
        notification_ids = []
        for notification_create in notifications:
            notification_id = await self.queue_notification(notification_create)
            notification_ids.append(notification_id)
        
        logger.info(f"Queued {len(notification_ids)} notifications in batch")
        return notification_ids
    
    async def process_notification(self, notification_id: str) -> bool:
        """
        Process a notification for delivery
        
        Args:
            notification_id: ID of the notification to deliver
            
        Returns:
            bool: True if successful, False otherwise
        """
        notification = await self.repo.get(notification_id)
        if not notification:
            logger.error(f"Notification {notification_id} not found")
            return False
            
        # Update status to sending
        notification.delivery_status = DeliveryStatus.SENDING
        await self.repo.update(notification_id, notification)
        
        # Get user subscription info
        user = await self.user_repo.get(notification.user_id)
        if not user or not user.push_token:
            logger.warning(f"User {notification.user_id} not found or has no push token")
            notification.delivery_status = DeliveryStatus.FAILED
            await self.repo.update(notification_id, notification)
            return False
            
        # Try to deliver the notification
        try:
            # Prepare the notification data to send
            push_data = {
                "title": notification.title,
                "body": notification.body,
                "icon": str(notification.image_url) if notification.image_url else None,
                "badge": settings.DEFAULT_NOTIFICATION_BADGE,
                "data": {
                    "url": str(notification.action_url) if notification.action_url else None,
                    "notification_id": notification_id,
                    "campaign_id": notification.campaign_id,
                    "custom_data": notification.personalized_data
                }
            }
            
            # If pywebpush is not available, just simulate delivery
            if not webpush:
                logger.warning("Simulating notification delivery (pywebpush not installed)")
                success = True
            else:
                # Actually send the notification
                response = webpush(
                    subscription_info=json.loads(user.push_token),
                    data=json.dumps(push_data),
                    vapid_private_key=settings.VAPID_PRIVATE_KEY,
                    vapid_claims=self.vapid_claims
                )
                success = response.status_code == 201
            
            # Update notification status
            if success:
                notification.delivery_status = DeliveryStatus.DELIVERED
                notification.delivered_at = datetime.now()
                logger.info(f"Notification {notification_id} delivered to user {notification.user_id}")
                audit_log(f"Delivered notification {notification_id} to user {notification.user_id}")
            else:
                notification.delivery_status = DeliveryStatus.FAILED
                logger.error(f"Failed to deliver notification {notification_id}")
                
            await self.repo.update(notification_id, notification)
            return success
                
        except Exception as e:
            logger.exception(f"Error delivering notification {notification_id}: {str(e)}")
            notification.delivery_status = DeliveryStatus.FAILED
            await self.repo.update(notification_id, notification)
            return False
    
    async def process_notifications_batch(self, notification_ids: List[str]) -> Dict[str, int]:
        """
        Process multiple notifications in batch
        
        Args:
            notification_ids: IDs of the notifications to deliver
            
        Returns:
            Dict[str, int]: Counts of succeeded, failed, etc.
        """
        results = {
            "total": len(notification_ids),
            "succeeded": 0,
            "failed": 0
        }
        
        for notification_id in notification_ids:
            success = await self.process_notification(notification_id)
            if success:
                results["succeeded"] += 1
            else:
                results["failed"] += 1
        
        logger.info(f"Batch processing completed: {results}")
        return results
    
    async def get_notification_status(self, notification_id: str) -> Optional[Dict[str, Any]]:
        """
        Get the status of a notification
        
        Args:
            notification_id: ID of the notification
            
        Returns:
            Optional[Dict[str, Any]]: Status information or None if not found
        """
        notification = await self.repo.get(notification_id)
        if not notification:
            return None
            
        return {
            "notification_id": notification.id,
            "status": notification.delivery_status,
            "queued_at": notification.created_at.isoformat() if notification.created_at else None,
            "delivered_at": notification.delivered_at.isoformat() if notification.delivered_at else None,
            "opened_at": notification.opened_at.isoformat() if notification.opened_at else None,
            "clicked_at": notification.clicked_at.isoformat() if notification.clicked_at else None
        }
    
    async def reset_notification_for_retry(self, notification_id: str) -> bool:
        """
        Reset a failed notification for retry
        
        Args:
            notification_id: ID of the notification to retry
            
        Returns:
            bool: True if successful, False otherwise
        """
        notification = await self.repo.get(notification_id)
        if not notification or notification.delivery_status != DeliveryStatus.FAILED:
            return False
            
        notification.delivery_status = DeliveryStatus.QUEUED
        notification.delivered_at = None
        notification.opened_at = None
        notification.clicked_at = None
        
        await self.repo.update(notification_id, notification)
        logger.info(f"Reset notification {notification_id} for retry")
        
        return True
    
    async def create_test_notification(self, notification: WebPushNotification, user_id: str) -> str:
        """
        Create a test notification for a user
        
        Args:
            notification: The notification content
            user_id: ID of the user to notify
            
        Returns:
            str: ID of the created notification
        """
        # Create a notification object
        new_notification = Notification(
            id=str(uuid.uuid4()),
            campaign_id="test_campaign",
            user_id=user_id,
            template_id="test_template",
            title=notification.title,
            body=notification.body,
            image_url=notification.image,
            action_url=notification.data.get("url") if notification.data else None,
            personalized_data=notification.data or {},
            delivery_status=DeliveryStatus.QUEUED,
            device_info={},
            notification_type=NotificationType.TEST
        )
        
        created = await self.repo.create(new_notification)
        logger.info(f"Test notification created: {created.id}")
        
        audit_log(f"Test notification created for user {user_id}")
        
        return created.id
    
    async def get_delivery_stats(self, campaign_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get notification delivery statistics
        
        Args:
            campaign_id: Optional campaign ID to filter by
            
        Returns:
            Dict[str, Any]: Delivery statistics
        """
        filters = {}
        if campaign_id:
            filters["campaign_id"] = campaign_id
            
        total = await self.repo.count(filters)
        
        # Get counts for each status
        status_counts = {}
        for status in DeliveryStatus:
            status_filters = filters.copy()
            status_filters["delivery_status"] = status
            status_counts[status.value] = await self.repo.count(status_filters)
        
        # Calculate percentages
        delivery_rate = (status_counts["delivered"] / total) * 100 if total > 0 else 0
        open_rate = (status_counts["opened"] / status_counts["delivered"]) * 100 if status_counts["delivered"] > 0 else 0
        click_rate = (status_counts["clicked"] / status_counts["opened"]) * 100 if status_counts["opened"] > 0 else 0
        
        return {
            "total": total,
            "status_counts": status_counts,
            "delivery_rate": round(delivery_rate, 2),
            "open_rate": round(open_rate, 2),
            "click_rate": round(click_rate, 2),
            "campaign_id": campaign_id,
            "timestamp": datetime.now().isoformat()
        }
    
    async def list_notifications_by_status(
        self, 
        status: DeliveryStatus, 
        skip: int = 0, 
        limit: int = 50,
        campaign_id: Optional[str] = None
    ) -> List[NotificationRead]:
        """
        List notifications by status
        
        Args:
            status: The delivery status to filter by
            skip: Number of records to skip for pagination
            limit: Maximum number of records to return
            campaign_id: Optional campaign ID to filter by
            
        Returns:
            List[NotificationRead]: Matching notifications
        """
        filters = {"delivery_status": status}
        if campaign_id:
            filters["campaign_id"] = campaign_id
            
        notifications = await self.repo.list(
            skip=skip,
            limit=limit,
            filters=filters
        )
        
        return [NotificationRead.model_validate(n) for n in notifications]
