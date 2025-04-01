import uuid
from datetime import datetime
from enum import Enum
from typing import Dict, Optional
from pydantic import BaseModel, Field, HttpUrl

class DeliveryStatus(str, Enum):
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"
    CLICKED = "clicked"

class Notification(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    campaign_id: str
    user_id: str
    template_id: str
    title: str
    body: str
    image_url: Optional[HttpUrl] = None
    action_url: Optional[HttpUrl] = None
    personalized_data: Dict = Field(default_factory=dict)
    sent_at: Optional[datetime] = None
    delivery_status: DeliveryStatus = DeliveryStatus.PENDING
    delivered_at: Optional[datetime] = None
    opened_at: Optional[datetime] = None
    clicked_at: Optional[datetime] = None
    device_info: Dict = Field(default_factory=dict)
    
    class Config:
        orm_mode = True
