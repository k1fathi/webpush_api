import uuid
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any

from pydantic import BaseModel, Field, HttpUrl

class DeliveryStatus(str, Enum):
    PENDING = "pending"
    QUEUED = "queued"
    SENDING = "sending"
    DELIVERED = "delivered"
    FAILED = "failed"
    OPENED = "opened"
    CLICKED = "clicked"

class NotificationType(str, Enum):
    CAMPAIGN = "campaign"
    TRIGGERED = "triggered"
    TRANSACTIONAL = "transactional"
    AUTOMATED = "automated"
    TEST = "test"

class Notification(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    campaign_id: str
    user_id: str
    template_id: str
    title: str
    body: str
    image_url: Optional[HttpUrl] = None
    action_url: Optional[HttpUrl] = None
    personalized_data: Dict[str, Any] = Field(default_factory=dict)
    sent_at: Optional[datetime] = None
    delivery_status: DeliveryStatus = DeliveryStatus.PENDING
    delivered_at: Optional[datetime] = None
    opened_at: Optional[datetime] = None
    clicked_at: Optional[datetime] = None
    device_info: Dict[str, Any] = Field(default_factory=dict)
    variant_id: Optional[str] = None
    notification_type: NotificationType = NotificationType.CAMPAIGN
    
    model_config = {"from_attributes": True}

class NotificationBase(BaseModel):
    """Base schema for notifications"""
    title: str
    body: str
    image_url: Optional[HttpUrl] = None
    action_url: Optional[HttpUrl] = None
    notification_type: NotificationType = NotificationType.CAMPAIGN
    
    model_config = {
        "from_attributes": True
    }

class NotificationCreate(NotificationBase):
    """Schema for creating notifications"""
    campaign_id: str
    user_id: str
    template_id: str
    personalized_data: Optional[Dict[str, Any]] = None
    variant_id: Optional[str] = None

class NotificationUpdate(BaseModel):
    """Schema for updating notifications"""
    title: Optional[str] = None
    body: Optional[str] = None
    image_url: Optional[HttpUrl] = None
    action_url: Optional[HttpUrl] = None
    delivery_status: Optional[DeliveryStatus] = None
    delivered_at: Optional[datetime] = None
    opened_at: Optional[datetime] = None
    clicked_at: Optional[datetime] = None
    device_info: Optional[Dict[str, Any]] = None

class NotificationRead(NotificationBase):
    """Schema for reading notifications"""
    id: str
    campaign_id: str
    user_id: str
    template_id: str
    personalized_data: Dict[str, Any]
    sent_at: Optional[datetime] = None
    delivery_status: DeliveryStatus
    delivered_at: Optional[datetime] = None
    opened_at: Optional[datetime] = None
    clicked_at: Optional[datetime] = None
    device_info: Dict[str, Any]
    variant_id: Optional[str] = None
    
    model_config = {
        "from_attributes": True
    }

class NotificationList(BaseModel):
    """Schema for listing notifications"""
    items: List[NotificationRead]
    total: int
    page: int
    page_size: int

class NotificationTrackEvent(BaseModel):
    """Schema for tracking notification events"""
    device_info: Optional[Dict[str, Any]] = None
    timestamp: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None
