import uuid
from datetime import datetime
from enum import Enum
from typing import Dict, Optional, Any
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
    
    model_config = {"from_attributes": True}  # Updated from orm_mode for Pydantic v2
