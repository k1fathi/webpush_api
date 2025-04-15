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
    DISMISSED = "dismissed"

class NotificationType(str, Enum):
    CAMPAIGN = "campaign"
    TRIGGERED = "triggered"
    TRANSACTIONAL = "transactional"
    AUTOMATED = "automated"
    TEST = "test"

class InteractionType(str, Enum):
    CLICK = "click"
    DISMISS = "dismiss"
    FOCUS = "focus"
    CLOSE = "close"

class Notification(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    campaign_id: Optional[str] = None
    user_id: Optional[str] = None
    subscription_id: Optional[str] = None
    template_id: Optional[str] = None
    title: str
    body: str
    
    # Web Push specific fields
    image_url: Optional[HttpUrl] = None
    icon_url: Optional[HttpUrl] = None
    badge_url: Optional[HttpUrl] = None
    action_url: Optional[HttpUrl] = None
    vibrate: Optional[List[int]] = None
    priority: Optional[int] = 0
    time_to_live: Optional[int] = None
    renotify: Optional[bool] = False
    silent: Optional[bool] = False
    require_interaction: Optional[bool] = False
    actions: Optional[List[Dict[str, Any]]] = None
    
    personalized_data: Dict[str, Any] = Field(default_factory=dict)
    sent_at: Optional[datetime] = None
    delivery_status: DeliveryStatus = DeliveryStatus.PENDING
    delivered_at: Optional[datetime] = None
    opened_at: Optional[datetime] = None
    clicked_at: Optional[datetime] = None
    dismissed_at: Optional[datetime] = None
    interacted_at: Optional[datetime] = None
    interaction_type: Optional[str] = None
    
    device_info: Dict[str, Any] = Field(default_factory=dict)
    variant_id: Optional[str] = None
    notification_type: NotificationType = NotificationType.CAMPAIGN
    
    # Delivery tracking
    delivery_attempts: Optional[int] = 0
    last_attempt_at: Optional[datetime] = None
    error_message: Optional[str] = None
    
    model_config = {"from_attributes": True}

class NotificationBase(BaseModel):
    """Base schema for notifications"""
    title: str
    body: str
    
    # Web Push specific optional fields
    image_url: Optional[HttpUrl] = None
    icon_url: Optional[HttpUrl] = None
    badge_url: Optional[HttpUrl] = None
    action_url: Optional[HttpUrl] = None
    vibrate: Optional[List[int]] = None
    priority: Optional[int] = 0
    time_to_live: Optional[int] = None
    renotify: Optional[bool] = False
    silent: Optional[bool] = False
    require_interaction: Optional[bool] = False
    actions: Optional[List[Dict[str, Any]]] = None
    
    notification_type: NotificationType = NotificationType.CAMPAIGN
    
    model_config = {
        "from_attributes": True
    }

class NotificationCreate(NotificationBase):
    """Schema for creating notifications"""
    campaign_id: Optional[str] = None
    user_id: Optional[str] = None
    subscription_id: Optional[str] = None
    template_id: Optional[str] = None
    personalized_data: Optional[Dict[str, Any]] = None
    variant_id: Optional[str] = None

class NotificationUpdate(BaseModel):
    """Schema for updating notifications"""
    title: Optional[str] = None
    body: Optional[str] = None
    image_url: Optional[HttpUrl] = None
    icon_url: Optional[HttpUrl] = None
    badge_url: Optional[HttpUrl] = None
    action_url: Optional[HttpUrl] = None
    
    delivery_status: Optional[DeliveryStatus] = None
    delivered_at: Optional[datetime] = None
    opened_at: Optional[datetime] = None
    clicked_at: Optional[datetime] = None
    dismissed_at: Optional[datetime] = None
    interacted_at: Optional[datetime] = None
    interaction_type: Optional[str] = None
    
    device_info: Optional[Dict[str, Any]] = None
    
    # Delivery tracking updates
    delivery_attempts: Optional[int] = None
    last_attempt_at: Optional[datetime] = None
    error_message: Optional[str] = None

class NotificationRead(NotificationBase):
    """Schema for reading notifications"""
    id: str
    campaign_id: Optional[str] = None
    user_id: Optional[str] = None
    subscription_id: Optional[str] = None
    template_id: Optional[str] = None
    personalized_data: Dict[str, Any]
    
    sent_at: Optional[datetime] = None
    delivery_status: DeliveryStatus
    delivered_at: Optional[datetime] = None
    opened_at: Optional[datetime] = None
    clicked_at: Optional[datetime] = None
    dismissed_at: Optional[datetime] = None
    interacted_at: Optional[datetime] = None
    interaction_type: Optional[str] = None
    
    device_info: Dict[str, Any]
    variant_id: Optional[str] = None
    
    # Delivery tracking
    delivery_attempts: int = 0
    last_attempt_at: Optional[datetime] = None
    error_message: Optional[str] = None
    
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
    event_type: str  # opened, clicked, dismissed, etc.
    notification_id: str
    subscription_id: Optional[str] = None
    device_info: Optional[Dict[str, Any]] = None
    timestamp: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None
    page_url: Optional[str] = None
    referrer: Optional[str] = None

class NotificationMetrics(BaseModel):
    """Schema for notification metrics"""
    sent_count: int
    delivered_count: int
    opened_count: int
    clicked_count: int
    dismissed_count: int
    failed_count: int
    
    delivery_rate: float  # delivered / sent
    open_rate: float  # opened / delivered
    click_rate: float  # clicked / opened
    dismiss_rate: float  # dismissed / opened
    
    avg_time_to_open: Optional[float] = None  # average time in seconds from delivery to open
    avg_time_to_click: Optional[float] = None  # average time in seconds from delivery to click
    
    metrics_by_browser: Dict[str, Dict[str, Any]] = Field(default_factory=dict)
    metrics_by_os: Dict[str, Dict[str, Any]] = Field(default_factory=dict)
    metrics_by_device: Dict[str, Dict[str, Any]] = Field(default_factory=dict)
    
    model_config = {
        "from_attributes": True
    }
