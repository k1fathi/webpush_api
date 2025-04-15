import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from uuid import UUID

from pywebpush import webpush, WebPushException
from sqlalchemy.orm import Session

from models.schemas.notification import Notification, DeliveryStatus
from models.schemas.subscription import SubscriptionRead, SubscriptionCreate, SubscriptionUpdate
from models.schemas.web_push_config import WebPushConfig
from models.schemas.web_push_event import WebPushEventCreate, InteractionEventType
from repositories.notification import NotificationRepository
from repositories.subscription import SubscriptionRepository
from repositories.web_push_config import WebPushConfigRepository
from repositories.web_push_event import WebPushEventRepository
from repositories.user import UserRepository
from utils.user_agent_parser import parse_user_agent

logger = logging.getLogger(__name__)

class WebPushService:
    """Service for handling web push notification functionality"""
    
    def __init__(self, db: Session):
        self.db = db
        self.config_repo = WebPushConfigRepository(db)
        self.event_repo = WebPushEventRepository(db)
        self.subscription_repo = SubscriptionRepository(db)
        self.user_repo = UserRepository(db)
    
    async def get_web_push_config(self, config_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get web push configuration
        
        Args:
            config_id: Optional config ID to fetch a specific config
            
        Returns:
            Web push configuration
        """
        if config_id:
            config = self.config_repo.get(config_id)
        else:
            config = self.config_repo.get_default_config()
            
        if not config:
            # Create a default config if none exists
            config = self.config_repo.create_default_config()
            
        return config
    
    async def create_subscription(self, subscription_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create or update a push subscription
        
        Args:
            subscription_data: Subscription data from browser
            
        Returns:
            Created/updated subscription
        """
        # Extract subscription details
        endpoint = subscription_data.get("endpoint")
        keys = subscription_data.get("keys", {})
        
        # Check if subscription already exists
        existing_subscription = self.subscription_repo.get_by_endpoint(endpoint)
        
        if existing_subscription:
            # Update existing subscription
            subscription_update = SubscriptionUpdate(
                permission_status="granted",
                is_active=True,
                metadata=subscription_data.get("metadata", {})
            )
            subscription = self.subscription_repo.update(
                existing_subscription.id,
                subscription_update
            )
            
            # Track subscription updated event
            await self.track_event("subscription_updated", {
                "subscription_id": str(subscription.id),
                "endpoint": endpoint
            })
            
            return {
                "id": str(subscription.id),
                "endpoint": subscription.endpoint,
                "created_at": subscription.created_at.isoformat(),
                "updated_at": subscription.updated_at.isoformat() if subscription.updated_at else None
            }
        
        # Parse user agent data
        user_agent = subscription_data.get("userAgent", "")
        ua_data = parse_user_agent(user_agent)
        
        # Create new subscription
        subscription_create = SubscriptionCreate(
            endpoint=endpoint,
            keys=keys,
            user_agent=user_agent,
            browser_name=ua_data.get("browser_name"),
            browser_version=ua_data.get("browser_version"),
            os_name=ua_data.get("os_name"),
            os_version=ua_data.get("os_version"),
            device_type=ua_data.get("device_type"),
            is_mobile=ua_data.get("is_mobile"),
            screen_resolution=subscription_data.get("screenResolution"),
            language=subscription_data.get("language"),
            metadata={
                "referrer": subscription_data.get("referrer"),
                "page_url": subscription_data.get("pageUrl"),
                "context": subscription_data.get("context", {})
            }
        )
        
        # Try to associate with user
        user_id = subscription_data.get("userId")
        if user_id:
            subscription_create.user_id = user_id
        
        # Create subscription
        subscription = self.subscription_repo.create(subscription_create)
        
        # Track subscription created event
        await self.track_event("subscription_created", {
            "subscription_id": str(subscription.id),
            "endpoint": endpoint,
            "browser": ua_data.get("browser_name"),
            "os": ua_data.get("os_name"),
            "device_type": ua_data.get("device_type")
        })
        
        return {
            "id": str(subscription.id),
            "endpoint": subscription.endpoint,
            "created_at": subscription.created_at.isoformat()
        }
    
    async def track_event(self, event_type: str, event_data: Dict[str, Any]) -> None:
        """
        Track a web push notification event
        
        Args:
            event_type: Type of event (shown, clicked, dismissed, etc.)
            event_data: Additional event data
        """
        try:
            # Parse user agent if provided
            user_agent = event_data.get("user_agent", "")
            ua_data = {}
            if user_agent:
                ua_data = parse_user_agent(user_agent)
            
            # Extract subscription information if provided
            subscription_data = event_data.get("subscription")
            subscription_id = None
            
            if subscription_data and isinstance(subscription_data, dict) and "endpoint" in subscription_data:
                # Look up subscription by endpoint
                subscription = self.subscription_repo.get_by_endpoint(subscription_data.get("endpoint"))
                if subscription:
                    subscription_id = subscription.id
                    # Update last used timestamp
                    self.subscription_repo.update_last_used(subscription.id)
            
            # Create event
            event_create = WebPushEventCreate(
                event_type=event_type,
                notification_id=event_data.get("notification_id"),
                subscription_id=subscription_id or event_data.get("subscription_id"),
                user_id=event_data.get("user_id"),
                campaign_id=event_data.get("campaign_id"),
                event_data=event_data,
                action_id=event_data.get("action"),
                page_url=event_data.get("url"),
                referrer=event_data.get("referrer"),
                user_agent=user_agent,
                browser_name=ua_data.get("browser_name"),
                browser_version=ua_data.get("browser_version"),
                os_name=ua_data.get("os_name"),
                os_version=ua_data.get("os_version"),
                device_type=ua_data.get("device_type"),
                screen_resolution=event_data.get("screen_resolution"),
                error_message=event_data.get("error_message"),
                error_code=event_data.get("error_code")
            )
            
            # Calculate time since sent/shown if applicable
            if event_type in ["clicked", "dismissed", "closed"] and "sent_at" in event_data:
                try:
                    sent_at = datetime.fromisoformat(event_data["sent_at"])
                    now = datetime.now()
                    event_create.time_since_sent = (now - sent_at).total_seconds()
                except (ValueError, TypeError):
                    pass
            
            # Save event
            self.event_repo.create(event_create)
            
        except Exception as e:
            logger.error(f"Error tracking web push event: {str(e)}")
    
    async def send_notification(
        self, 
        notification: Notification, 
        subscription: Union[Dict[str, Any], Any]
    ) -> bool:
        """
        Send a web push notification to a subscription
        
        Args:
            notification: Notification data
            subscription: Subscription object or data
            
        Returns:
            Success status
        """
        try:
            # Get config for VAPID details
            config = await self.get_web_push_config()
            
            # Prepare notification payload
            payload = {
                "notification": {
                    "title": notification.title,
                    "body": notification.body,
                    "icon": notification.icon_url or config.get("default_icon_url"),
                    "badge": notification.badge_url or config.get("default_badge_url"),
                    "image": notification.image_url,
                    "data": {
                        "url": notification.action_url,
                        "id": str(notification.id) if notification.id else str(uuid.uuid4()),
                        "campaignId": str(notification.campaign_id) if notification.campaign_id else None,
                        "userId": str(notification.user_id) if notification.user_id else None,
                        "sentAt": datetime.now().isoformat(),
                        "ttl": notification.time_to_live,
                        "personalized": notification.personalized_data or {}
                    },
                    "requireInteraction": notification.require_interaction or config.get("default_require_interaction"),
                    "silent": notification.silent or config.get("default_silent"),
                    "renotify": notification.renotify or config.get("default_renotify"),
                    "vibrate": notification.vibrate or config.get("default_vibrate_pattern")
                }
            }
            
            # Add actions if provided
            if notification.actions:
                payload["notification"]["actions"] = notification.actions
            
            # Get subscription data
            subscription_data = None
            subscription_id = None
            
            if isinstance(subscription, dict):
                # Direct subscription data
                subscription_data = subscription
                # Try to find subscription in DB
                if "endpoint" in subscription:
                    db_subscription = self.subscription_repo.get_by_endpoint(subscription["endpoint"])
                    if db_subscription:
                        subscription_id = db_subscription.id
            else:
                # Subscription model object
                subscription_id = subscription.id
                subscription_data = {
                    "endpoint": subscription.endpoint,
                    "keys": subscription.keys
                }
            
            if not subscription_data or "endpoint" not in subscription_data:
                logger.error("Invalid subscription data")
                return False

            # Send push notification
            response = webpush(
                subscription_info=subscription_data,
                data=json.dumps(payload),
                vapid_private_key=config.get("vapid_private_key"),
                vapid_claims={
                    "sub": f"mailto:{config.get('vapid_subject')}"
                },
                ttl=notification.time_to_live or 86400  # Default 24 hours
            )
            
            # Track sent event
            await self.track_event("sent", {
                "notification_id": str(notification.id) if notification.id else None,
                "subscription_id": str(subscription_id) if subscription_id else None,
                "user_id": str(notification.user_id) if notification.user_id else None,
                "campaign_id": str(notification.campaign_id) if notification.campaign_id else None,
                "title": notification.title,
                "body": notification.body,
                "payload": payload
            })
            
            return response.ok
            
        except WebPushException as e:
            logger.error(f"WebPush error: {str(e)}")
            
            # Check if subscription is expired/invalid
            if e.response and e.response.status_code in [404, 410]:
                logger.info(f"Subscription expired or invalid: {subscription_data.get('endpoint')}")
                
                # Mark subscription as inactive if we have the ID
                if subscription_id:
                    self.subscription_repo.update(
                        subscription_id,
                        SubscriptionUpdate(is_active=False)
                    )
                
                # Track error event
                await self.track_event("error", {
                    "error_type": "subscription_expired",
                    "notification_id": str(notification.id) if notification.id else None,
                    "subscription_id": str(subscription_id) if subscription_id else None,
                    "error_message": str(e),
                    "status_code": e.response.status_code if e.response else None
                })
            else:
                # Track generic error
                await self.track_event("error", {
                    "error_type": "send_failed",
                    "notification_id": str(notification.id) if notification.id else None,
                    "subscription_id": str(subscription_id) if subscription_id else None,
                    "error_message": str(e),
                    "status_code": e.response.status_code if e.response else None
                })
                
            return False
            
        except Exception as e:
            logger.error(f"Error sending web push notification: {str(e)}")
            
            # Track error
            await self.track_event("error", {
                "error_type": "exception",
                "notification_id": str(notification.id) if notification.id else None,
                "subscription_id": str(subscription_id) if subscription_id else None,
                "error_message": str(e)
            })
            
            return False