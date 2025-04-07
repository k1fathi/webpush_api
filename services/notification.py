import logging
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any

from core.config import settings
from models.schemas.notification import Notification, DeliveryStatus, NotificationType
from repositories.notification import NotificationRepository
from repositories.campaign import CampaignRepository
from repositories.template import TemplateRepository
from repositories.user import UserRepository
from services.cep import CepService
from utils.audit import audit_log

logger = logging.getLogger(__name__)

class NotificationService:
    """Service for managing notifications according to the notification delivery flow"""
    
    def __init__(self):
        self.notification_repo = NotificationRepository()
        self.campaign_repo = CampaignRepository()
        self.template_repo = TemplateRepository()
        self.user_repo = UserRepository()
        self.delivery_repo = NotificationDeliveryRepository()
        self.cep_service = CepService()
        
    async def create_notification(self, notification_data: Dict) -> Notification:
        """
        Create a new notification
        
        Args:
            notification_data: Dictionary with notification data
            
        Returns:
            Notification: The created notification
        """
        # Create the notification object
        notification = Notification(
            id=str(uuid.uuid4()),
            **notification_data
        )
        
        # Save to repository
        created_notification = await self.notification_repo.create(notification)
        
        # Log the creation
        audit_log(f"Created notification {created_notification.id} for user {notification.user_id}")
        
        return created_notification
    
    async def create_notifications_for_campaign(
        self, 
        campaign_id: str, 
        user_ids: List[str]
    ) -> List[Notification]:
        """
        Create notifications for a campaign targeting multiple users
        
        Args:
            campaign_id: The campaign ID
            user_ids: List of user IDs to target
            
        Returns:
            List[Notification]: The created notifications
        """
        # Get the campaign
        campaign = await self.campaign_repo.get(campaign_id)
        if not campaign:
            raise ValueError(f"Campaign with ID {campaign_id} not found")
            
        # Get the template
        if not campaign.template_id:
            raise ValueError(f"Campaign {campaign_id} has no template")
            
        template = await self.template_repo.get(campaign.template_id)
        if not template:
            raise ValueError(f"Template {campaign.template_id} not found")
            
        notifications = []
        
        # Create a notification for each user
        for user_id in user_ids:
            # Get user for personalization
            user = await self.user_repo.get(user_id)
            if not user:
                logger.warning(f"User {user_id} not found, skipping notification creation")
                continue
                
            # Personalize content
            title, body = await self._personalize_content(
                template.title, 
                template.body, 
                user
            )
            
            # Create notification
            notification = await self.create_notification({
                "campaign_id": campaign_id,
                "user_id": user_id,
                "template_id": template.id,
                "title": title,
                "body": body,
                "image_url": template.image_url,
                "action_url": template.action_url,
                "delivery_status": DeliveryStatus.PENDING,
                "notification_type": NotificationType.CAMPAIGN
            })
            
            notifications.append(notification)
            
        audit_log(f"Created {len(notifications)} notifications for campaign {campaign_id}")
        return notifications
    
    async def _personalize_content(
        self,
        title: str,
        body: str,
        user: Any
    ) -> tuple[str, str]:
        """Personalize notification content for a user"""
        # Basic personalization with user attributes
        personalized_title = title
        personalized_body = body
        
        if user:
            # Replace user attributes in title and body
            replacements = {
                "{name}": user.name,
                "{email}": user.email,
                "{first_name}": user.name.split()[0] if user.name else ""
            }
            
            # Add custom attributes
            if hasattr(user, 'custom_attributes') and user.custom_attributes:
                for key, value in user.custom_attributes.items():
                    if isinstance(value, (str, int, float)):
                        replacements[f"{{{key}}}"] = str(value)
            
            # Apply replacements
            for placeholder, value in replacements.items():
                personalized_title = personalized_title.replace(placeholder, str(value))
                personalized_body = personalized_body.replace(placeholder, str(value))
                
        return personalized_title, personalized_body
        
    async def send_notification(self, notification_id: str) -> bool:
        """
        Send a notification through the appropriate channel
        
        This is the entry point for the notification delivery flow
        
        Args:
            notification_id: The notification ID to send
            
        Returns:
            bool: Whether sending was successful
        """
        # Get the notification
        notification = await self.notification_repo.get(notification_id)
        if not notification:
            raise ValueError(f"Notification {notification_id} not found")
            
        # Mark as sending
        notification = await self.notification_repo.mark_as_sent(notification_id)
        
        try:
            # Create delivery tracking record
            delivery = await self.delivery_repo.create({
                "notification_id": notification_id,
                "user_id": notification.user_id,
                "status": "sending",
                "attempt_count": 1,
                "first_attempt_time": datetime.now()
            })
            
            # This is where we'd integrate with the push service
            # For now, we'll just simulate sending
            logger.info(f"Sending notification {notification_id} to user {notification.user_id}")
            
            # In a real implementation, you'd call the push service here
            # result = push_service.send(notification.user_id, notification.title, notification.body)
            
            # For simulating delivery success
            result = True
            
            if result:
                # Mark as delivered
                await self.notification_repo.mark_as_delivered(notification_id)
                await self.delivery_repo.mark_as_delivered(delivery.id)
                
                # Queue analytics tracking
                from tasks.notification_tasks import track_notification_delivery
                track_notification_delivery.delay(notification_id)
                
                audit_log(f"Successfully sent notification {notification_id}")
                return True
            else:
                # Mark as failed
                await self.notification_repo.mark_as_failed(notification_id, "Delivery failure")
                await self.delivery_repo.mark_as_failed(delivery.id, "Delivery failure")
                
                audit_log(f"Failed to send notification {notification_id}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending notification {notification_id}: {str(e)}")
            
            # Mark as failed with error message
            await self.notification_repo.mark_as_failed(notification_id, str(e))
            
            # If delivery record was created, mark it as failed too
            try:
                await self.delivery_repo.mark_for_retry(
                    delivery.id, 
                    str(e),
                    retry_reason="connection_error"
                )
            except:
                logger.error(f"Could not update delivery record for notification {notification_id}")
                
            return False
    
    async def track_open(self, notification_id: str) -> bool:
        """
        Track when a notification is opened
        
        Args:
            notification_id: The notification ID
            
        Returns:
            bool: Success status
        """
        notification = await self.notification_repo.get(notification_id)
        if not notification:
            logger.warning(f"Notification {notification_id} not found for open tracking")
            return False
            
        # Mark as opened
        await self.notification_repo.mark_as_opened(notification_id)
        
        # Track analytics
        from tasks.notification_tasks import track_notification_open
        track_notification_open.delay(notification_id)
        
        audit_log(f"Tracked open for notification {notification_id}")
        return True
    
    async def track_click(self, notification_id: str) -> bool:
        """
        Track when a notification is clicked
        
        Args:
            notification_id: The notification ID
            
        Returns:
            bool: Success status
        """
        notification = await self.notification_repo.get(notification_id)
        if not notification:
            logger.warning(f"Notification {notification_id} not found for click tracking")
            return False
            
        # Mark as clicked
        await self.notification_repo.mark_as_clicked(notification_id)
        
        # Track analytics
        from tasks.notification_tasks import track_notification_click
        track_notification_click.delay(notification_id)
        
        audit_log(f"Tracked click for notification {notification_id}")
        return True
    
    async def get_notification_stats(self, campaign_id: str) -> Dict:
        """
        Get statistics for notifications in a campaign
        
        Args:
            campaign_id: The campaign ID
            
        Returns:
            Dict: Notification statistics
        """
        return await self.notification_repo.get_stats_by_campaign(campaign_id)
        
    async def get_notification(self, notification_id: str) -> Optional[Notification]:
        """
        Get a notification by ID
        
        Args:
            notification_id: The notification ID
            
        Returns:
            Optional[Notification]: The notification if found
        """
        return await self.notification_repo.get(notification_id)
    
    async def get_notifications_for_user(
        self, 
        user_id: str, 
        skip: int = 0, 
        limit: int = 20
    ) -> List[Notification]:
        """
        Get notifications for a user
        
        Args:
            user_id: The user ID
            skip: Number of items to skip
            limit: Maximum number of items to return
            
        Returns:
            List[Notification]: List of notifications
        """
        return await self.notification_repo.get_by_user(user_id, skip, limit)
    
    async def get_notifications_by_customer_id(
        self, 
        customer_id: str,
        skip: int = 0, 
        limit: int = 20,
        status: Optional[DeliveryStatus] = None
    ) -> List[Dict[str, Any]]:
        """
        Get notifications for a specific customer ID
        
        Args:
            customer_id: The customer ID to filter by
            skip: Number of items to skip
            limit: Maximum number of items to return
            status: Optional status filter
            
        Returns:
            List[Dict[str, Any]]: List of notification data
        """
        # Get users associated with this customer ID
        users = await self.user_repo.get_users_by_customer_id(customer_id)
        
        if not users:
            logger.warning(f"No users found for customer ID: {customer_id}")
            return []
            
        user_ids = [str(user.id) for user in users]
        
        # Get notifications for these users
        notifications = []
        
        for user_id in user_ids:
            user_notifications = await self.notification_repo.get_by_user(
                user_id=user_id, 
                limit=limit
            )
            
            # Filter by status if specified
            if status:
                user_notifications = [n for n in user_notifications if n.delivery_status == status]
                
            # Transform to dictionary for consistent response format
            for notification in user_notifications:
                notification_dict = notification.model_dump()
                # Add additional data if needed
                notification_dict["user_email"] = next(
                    (user.email for user in users if str(user.id) == notification.user_id),
                    None
                )
                notifications.append(notification_dict)
        
        # Apply pagination
        return notifications[skip:skip+limit]
