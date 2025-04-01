import logging
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Union

from fastapi.encoders import jsonable_encoder

from core.config import settings
from models.analytics import Analytics, ConversionType
from models.domain.notification import NotificationModel
from repositories.analytics import AnalyticsRepository
from repositories.campaign import CampaignRepository
from repositories.notification import NotificationRepository
from repositories.user import UserRepository
from services.cdp import CdpService
from utils.audit import audit_log

logger = logging.getLogger(__name__)

class AnalyticsService:
    def __init__(self):
        self.analytics_repo = AnalyticsRepository()
        self.notification_repo = NotificationRepository()
        self.campaign_repo = CampaignRepository()
        self.user_repo = UserRepository()
        self.cdp_service = CdpService()

    async def record_send(self, notification_id: str) -> Analytics:
        """
        Record a notification send event
        """
        notification = await self.notification_repo.get(notification_id)
        if not notification:
            raise ValueError(f"Notification {notification_id} not found")

        # Create analytics event
        analytics_event = Analytics(
            id=str(uuid.uuid4()),
            notification_id=notification_id,
            campaign_id=notification.campaign_id,
            user_id=notification.user_id,
            delivered=False,  # Not delivered yet
            opened=False,
            clicked=False,
            event_time=datetime.now(),
            user_action="send",
        )

        # Save the analytics event
        created_event = await self.analytics_repo.create(analytics_event)
        
        # Trigger event queue
        from tasks.analytics_tasks import process_analytics_event
        process_analytics_event.delay(str(created_event.id), "send")
        
        audit_log(f"Recorded send event for notification {notification_id}")
        return created_event

    async def record_delivery(self, notification_id: str) -> Analytics:
        """
        Record a notification delivery event
        """
        notification = await self.notification_repo.get(notification_id)
        if not notification:
            raise ValueError(f"Notification {notification_id} not found")
        
        # Create or update analytics event
        existing_event = await self.analytics_repo.get_by_notification(notification_id)
        if existing_event:
            existing_event.delivered = True
            existing_event.event_time = datetime.now()
            updated_event = await self.analytics_repo.update(existing_event.id, existing_event)
            
            # Trigger event queue
            from tasks.analytics_tasks import process_analytics_event
            process_analytics_event.delay(str(updated_event.id), "delivery")
            
            audit_log(f"Updated delivery event for notification {notification_id}")
            return updated_event
        else:
            # Create new event
            analytics_event = Analytics(
                id=str(uuid.uuid4()),
                notification_id=notification_id,
                campaign_id=notification.campaign_id,
                user_id=notification.user_id,
                delivered=True,
                opened=False,
                clicked=False,
                event_time=datetime.now(),
                user_action="delivery",
            )
            
            created_event = await self.analytics_repo.create(analytics_event)
            
            # Trigger event queue
            from tasks.analytics_tasks import process_analytics_event
            process_analytics_event.delay(str(created_event.id), "delivery")
            
            audit_log(f"Recorded delivery event for notification {notification_id}")
            return created_event

    async def record_open(self, notification_id: str) -> Analytics:
        """
        Record a notification open event
        """
        notification = await self.notification_repo.get(notification_id)
        if not notification:
            raise ValueError(f"Notification {notification_id} not found")
        
        # Create or update analytics event
        existing_event = await self.analytics_repo.get_by_notification(notification_id)
        if existing_event:
            existing_event.opened = True
            existing_event.event_time = datetime.now()
            updated_event = await self.analytics_repo.update(existing_event.id, existing_event)
            
            # Trigger event queue
            from tasks.analytics_tasks import process_analytics_event
            process_analytics_event.delay(str(updated_event.id), "open")
            
            audit_log(f"Updated open event for notification {notification_id}")
            return updated_event
        else:
            # Create new event
            analytics_event = Analytics(
                id=str(uuid.uuid4()),
                notification_id=notification_id,
                campaign_id=notification.campaign_id,
                user_id=notification.user_id,
                delivered=True,  # Assume delivered if opened
                opened=True,
                clicked=False,
                event_time=datetime.now(),
                user_action="open",
            )
            
            created_event = await self.analytics_repo.create(analytics_event)
            
            # Trigger event queue
            from tasks.analytics_tasks import process_analytics_event
            process_analytics_event.delay(str(created_event.id), "open")
            
            audit_log(f"Recorded open event for notification {notification_id}")
            return created_event

    async def record_click(self, notification_id: str) -> Analytics:
        """
        Record a notification click event
        """
        notification = await self.notification_repo.get(notification_id)
        if not notification:
            raise ValueError(f"Notification {notification_id} not found")
        
        # Create or update analytics event
        existing_event = await self.analytics_repo.get_by_notification(notification_id)
        if existing_event:
            existing_event.clicked = True
            existing_event.opened = True  # Click implies open
            existing_event.event_time = datetime.now()
            existing_event.user_action = "click"
            updated_event = await self.analytics_repo.update(existing_event.id, existing_event)
            
            # Trigger event queue
            from tasks.analytics_tasks import process_analytics_event
            process_analytics_event.delay(str(updated_event.id), "click")
            
            audit_log(f"Updated click event for notification {notification_id}")
            return updated_event
        else:
            # Create new event
            analytics_event = Analytics(
                id=str(uuid.uuid4()),
                notification_id=notification_id,
                campaign_id=notification.campaign_id,
                user_id=notification.user_id,
                delivered=True,  # Assume delivered if clicked
                opened=True,     # Click implies open
                clicked=True,
                event_time=datetime.now(),
                user_action="click",
            )
            
            created_event = await self.analytics_repo.create(analytics_event)
            
            # Trigger event queue
            from tasks.analytics_tasks import process_analytics_event
            process_analytics_event.delay(str(created_event.id), "click")
            
            audit_log(f"Recorded click event for notification {notification_id}")
            return created_event

    async def record_conversion(
        self, 
        notification_id: str, 
        conversion_type: ConversionType, 
        value: float = 0.0
    ) -> Analytics:
        """
        Record a conversion event from a notification
        """
        notification = await self.notification_repo.get(notification_id)
        if not notification:
            raise ValueError(f"Notification {notification_id} not found")
        
        # Create or update analytics event
        existing_event = await self.analytics_repo.get_by_notification(notification_id)
        if existing_event:
            existing_event.clicked = True  # Assume clicked if converted
            existing_event.opened = True   # Assume opened if converted
            existing_event.event_time = datetime.now()
            existing_event.user_action = "conversion"
            existing_event.conversion_type = conversion_type
            existing_event.conversion_value = value
            
            updated_event = await self.analytics_repo.update(existing_event.id, existing_event)
            
            # Trigger event queue
            from tasks.analytics_tasks import process_analytics_event
            process_analytics_event.delay(str(updated_event.id), "conversion")
            
            audit_log(f"Updated conversion event for notification {notification_id}")
            return updated_event
        else:
            # Create new event
            analytics_event = Analytics(
                id=str(uuid.uuid4()),
                notification_id=notification_id,
                campaign_id=notification.campaign_id,
                user_id=notification.user_id,
                delivered=True,  # Assume delivered if converted
                opened=True,     # Assume opened if converted
                clicked=True,    # Assume clicked if converted
                event_time=datetime.now(),
                user_action="conversion",
                conversion_type=conversion_type,
                conversion_value=value
            )
            
            created_event = await self.analytics_repo.create(analytics_event)
            
            # Trigger event queue
            from tasks.analytics_tasks import process_analytics_event
            process_analytics_event.delay(str(created_event.id), "conversion")
            
            audit_log(f"Recorded conversion event for notification {notification_id}")
            return created_event
    
    async def record_failure(self, notification_id: str, reason: str = None) -> Analytics:
        """
        Record a notification failure event
        """
        notification = await self.notification_repo.get(notification_id)
        if not notification:
            raise ValueError(f"Notification {notification_id} not found")
        
        # Create new analytics event
        analytics_event = Analytics(
            id=str(uuid.uuid4()),
            notification_id=notification_id,
            campaign_id=notification.campaign_id,
            user_id=notification.user_id,
            delivered=False,
            opened=False,
            clicked=False,
            event_time=datetime.now(),
            user_action=f"failure:{reason}" if reason else "failure",
        )
        
        created_event = await self.analytics_repo.create(analytics_event)
        
        # Trigger event queue
        from tasks.analytics_tasks import process_analytics_event
        process_analytics_event.delay(str(created_event.id), "failure")
        
        audit_log(f"Recorded failure event for notification {notification_id}")
        return created_event
    
    async def get_campaign_statistics(self, campaign_id: str) -> Dict:
        """
        Get statistics for a campaign
        """
        # Verify campaign exists
        campaign = await self.campaign_repo.get(campaign_id)
        if not campaign:
            raise ValueError(f"Campaign {campaign_id} not found")
            
        # Get all analytics events for this campaign
        events = await self.analytics_repo.get_by_campaign(campaign_id)
        
        # Calculate statistics
        total_sent = await self.notification_repo.count_by_campaign(campaign_id)
        total_delivered = sum(1 for e in events if e.delivered)
        total_opened = sum(1 for e in events if e.opened)
        total_clicked = sum(1 for e in events if e.clicked)
        total_conversions = sum(1 for e in events if e.conversion_type)
        
        # Calculate rates
        delivery_rate = total_delivered / total_sent if total_sent > 0 else 0
        open_rate = total_opened / total_delivered if total_delivered > 0 else 0
        click_rate = total_clicked / total_opened if total_opened > 0 else 0
        conversion_rate = total_conversions / total_clicked if total_clicked > 0 else 0
        
        # Group conversions by type
        conversion_types = {}
        for event in events:
            if event.conversion_type:
                conversion_type = event.conversion_type.value
                if conversion_type not in conversion_types:
                    conversion_types[conversion_type] = {
                        "count": 0,
                        "value": 0
                    }
                conversion_types[conversion_type]["count"] += 1
                conversion_types[conversion_type]["value"] += event.conversion_value
        
        # Calculate time-based metrics
        # Average time from delivery to open
        open_times = []
        for event in events:
            if event.opened and event.delivered:
                notification = await self.notification_repo.get(event.notification_id)
                if notification and notification.delivered_at and notification.opened_at:
                    open_time = (notification.opened_at - notification.delivered_at).total_seconds()
                    open_times.append(open_time)
                    
        avg_time_to_open = sum(open_times) / len(open_times) if open_times else 0
        
        # Return statistics
        return {
            "campaign_id": campaign_id,
            "total_notifications": total_sent,
            "delivered": total_delivered,
            "opened": total_opened,
            "clicked": total_clicked,
            "conversions": total_conversions,
            "delivery_rate": delivery_rate,
            "open_rate": open_rate,
            "click_rate": click_rate,
            "conversion_rate": conversion_rate,
            "conversion_types": conversion_types,
            "avg_time_to_open": avg_time_to_open,
            "calculated_at": datetime.now()
        }
        
    async def sync_with_cdp(self, analytics_event_id: str) -> bool:
        """
        Sync analytics data with the CDP
        """
        if not self.cdp_service.is_enabled():
            return False
            
        event = await self.analytics_repo.get(analytics_event_id)
        if not event:
            logger.error(f"Analytics event {analytics_event_id} not found")
            return False
            
        user = await self.user_repo.get(event.user_id)
        notification = await self.notification_repo.get(event.notification_id)
        
        if not user or not notification:
            logger.error(f"Missing user or notification data for analytics event {analytics_event_id}")
            return False
            
        # Prepare data for CDP
        cdp_data = {
            "user_id": str(event.user_id),
            "event_type": event.user_action,
            "timestamp": event.event_time.isoformat(),
            "properties": {
                "notification_id": str(event.notification_id),
                "campaign_id": str(event.campaign_id),
                "delivered": event.delivered,
                "opened": event.opened,
                "clicked": event.clicked,
            }
        }
        
        if event.conversion_type:
            cdp_data["properties"]["conversion_type"] = event.conversion_type.value
            cdp_data["properties"]["conversion_value"] = event.conversion_value
            
        # Send to CDP
        success = await self.cdp_service.track_event(cdp_data)
        
        if success:
            audit_log(f"Synced analytics event {analytics_event_id} with CDP")
        else:
            logger.error(f"Failed to sync analytics event {analytics_event_id} with CDP")
            
        return success
