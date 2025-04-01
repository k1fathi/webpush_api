import uuid
from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field, HttpUrl

class WebhookEventType(str, Enum):
    NOTIFICATION_SENT = "notification_sent"
    NOTIFICATION_DELIVERED = "notification_delivered"
    NOTIFICATION_CLICKED = "notification_clicked"
    NOTIFICATION_FAILED = "notification_failed"
    USER_SUBSCRIBED = "user_subscribed"
    USER_UNSUBSCRIBED = "user_unsubscribed"

class Webhook(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    endpoint_url: HttpUrl
    event_type: WebhookEventType
    secret_key: str
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.now)
    last_triggered_at: Optional[datetime] = None
    
    class Config:
        orm_mode = True
