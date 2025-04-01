import json
import logging
import time
from datetime import datetime
from typing import Dict, List, Optional, Union

import pywebpush
from pywebpush import WebPushException

from core.config import settings
from models.domain.notification import NotificationModel, DeliveryStatus
from models.domain.user import UserModel
from repositories.notification import NotificationRepository
from repositories.user import UserRepository
from utils.audit import audit_log

logger = logging.getLogger(__name__)

class WebPushService:
    def __init__(self):
        self.vapid_private_key = settings.VAPID_PRIVATE_KEY
        self.vapid_public_key = settings.VAPID_PUBLIC_KEY
        self.vapid_claims = {"sub": settings.VAPID_CLAIMS_EMAIL}
        self.notification_repo = NotificationRepository()
        self.user_repo = UserRepository()
    
    def get_vapid_public_key(self) -> str:
        """Get the VAPID public key for browser subscription"""
        return self.vapid_public_key
    
    def personalize_notification(self, notification: NotificationModel, user: UserModel) -> NotificationModel:
        """
        Personalize notification content with user data
        """
        # Replace dynamic variables in title and body
        title = notification.title
        body = notification.body
        
        # Basic personalization with user attributes
        replacements = {
            "{name}": user.name,
            "{email}": user.email,
            "{first_name}": user.name.split(" ")[0] if user.name else "",
        }
        
        # Add custom attributes from user
        for key, value in user.custom_attributes.items():
            if isinstance(value, (str, int, float)):
                replacements[f"{{{key}}}"] = str(value)
        
        # Apply replacements
        for placeholder, value in replacements.items():
            title = title.replace(placeholder, value)
            body = body.replace(placeholder, value)
        
        # Update notification
        notification.title = title
        notification.body = body
        notification.personalized_data = replacements
        
        return notification
    
    def send(self, notification: NotificationModel, user: UserModel) -> bool:
        """
        Send a web push notification to a user
        
        Returns True if successful, False otherwise
        """
        if not user.push_token:
            logger.warning(f"User {user.id} has no push token")
            return False
        
        try:
            # Parse the subscription info
            subscription_info = json.loads(user.push_token)
            
            # Prepare payload
            payload = {
                "title": notification.title,
                "body": notification.body,
                "icon": notification.image_url if notification.image_url else None,
                "url": notification.action_url if notification.action_url else None,
                "notificationId": str(notification.id),
                "timestamp": int(time.time())
            }
            
            # Add tracking info
            tracking_url = f"{settings.API_PREFIX}/webpush/track/{notification.id}"
            payload["trackingUrl"] = tracking_url
            
            # Send the notification
            response = pywebpush.webpush(
                subscription_info=subscription_info,
                data=json.dumps(payload),
                vapid_private_key=self.vapid_private_key,
                vapid_claims=self.vapid_claims
            )
            
            # Log the send attempt
            logger.info(f"Push notification sent to user {user.id}, status: {response.status_code}")
            audit_log(f"Push notification {notification.id} sent to user {user.id}")
            
            # Return success based on status code
            return 200 <= response.status_code < 300
            
        except WebPushException as e:
            logger.error(f"WebPush failed for user {user.id}: {str(e)}")
            
            # Check for subscription expired/invalid
            if e.response and e.response.status_code in (404, 410):
                logger.info(f"Subscription for user {user.id} is expired or invalid, clearing token")
                user.push_token = None
                self.user_repo.update(user)
                
            return False
            
        except Exception as e:
            logger.error(f"Failed to send notification to user {user.id}: {str(e)}")
            return False
    
    def track_open(self, notification_id: str) -> bool:
        """Track when a notification is opened"""
        notification = self.notification_repo.get(notification_id)
        if not notification:
            return False
        
        notification.opened_at = datetime.utcnow()
        self.notification_repo.update(notification)
        
        return True
    
    def track_click(self, notification_id: str) -> bool:
        """Track when a notification is clicked"""
        notification = self.notification_repo.get(notification_id)
        if not notification:
            return False
        
        notification.clicked_at = datetime.utcnow()
        notification.delivery_status = DeliveryStatus.CLICKED
        self.notification_repo.update(notification)
        
        return True
