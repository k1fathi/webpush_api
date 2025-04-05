from datetime import datetime
from typing import Dict, List, Optional, Any

from models.schemas.notification import Notification, DeliveryStatus

class NotificationRepository:
    """Repository for notification operations"""
    
    def __init__(self, db=None):
        self.db = db
        # For simplicity, using in-memory storage for now
        # In a real implementation, this would use a database
        self._notifications = {}
    
    async def create(self, notification: Notification) -> Notification:
        """Create a new notification"""
        if not notification.id:
            import uuid
            notification.id = str(uuid.uuid4())
            
        # Set timestamps
        now = datetime.now()
        notification.created_at = now
        
        self._notifications[notification.id] = notification
        return notification
    
    async def get(self, notification_id: str) -> Optional[Notification]:
        """Get a notification by ID"""
        return self._notifications.get(notification_id)
    
    async def update(self, notification_id: str, notification: Notification) -> Optional[Notification]:
        """Update an existing notification"""
        if notification_id not in self._notifications:
            return None
        
        self._notifications[notification_id] = notification
        return notification
    
    async def delete(self, notification_id: str) -> bool:
        """Delete a notification"""
        if notification_id not in self._notifications:
            return False
        
        del self._notifications[notification_id]
        return True
    
    async def list(
        self, 
        skip: int = 0, 
        limit: int = 100,
        filters: Dict[str, Any] = None
    ) -> List[Notification]:
        """List notifications with optional filtering"""
        notifications = list(self._notifications.values())
        
        # Apply filters if provided
        if filters:
            for k, v in filters.items():
                notifications = [n for n in notifications if getattr(n, k) == v]
        
        # Apply pagination
        return notifications[skip : skip + limit]
    
    async def count(self, filters: Dict[str, Any] = None) -> int:
        """Count notifications with optional filtering"""
        notifications = list(self._notifications.values())
        
        # Apply filters if provided
        if filters:
            for k, v in filters.items():
                notifications = [n for n in notifications if getattr(n, k) == v]
                
        return len(notifications)
    
    async def get_by_user(self, user_id: str, limit: int = 50) -> List[Notification]:
        """Get notifications for a specific user"""
        return [
            n for n in self._notifications.values()
            if n.user_id == user_id
        ][:limit]
    
    async def mark_as_delivered(self, notification_id: str) -> bool:
        """Mark a notification as delivered"""
        notification = self._notifications.get(notification_id)
        if not notification:
            return False
        
        notification.delivery_status = DeliveryStatus.DELIVERED
        notification.delivered_at = datetime.now()
        return True
    
    async def mark_as_opened(self, notification_id: str) -> bool:
        """Mark a notification as opened"""
        notification = self._notifications.get(notification_id)
        if not notification:
            return False
        
        notification.delivery_status = DeliveryStatus.OPENED
        notification.opened_at = datetime.now()
        return True
    
    async def mark_as_clicked(self, notification_id: str) -> bool:
        """Mark a notification as clicked"""
        notification = self._notifications.get(notification_id)
        if not notification:
            return False
        
        notification.delivery_status = DeliveryStatus.CLICKED
        notification.clicked_at = datetime.now()
        return True
