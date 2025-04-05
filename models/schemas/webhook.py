import uuid
from datetime import datetime
from enum import Enum
from typing import Optional, Dict, List, Any
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
    
    model_config = {"from_attributes": True}

class WebhookBase(BaseModel):
    """Base schema for webhooks"""
    name: str
    endpoint_url: HttpUrl
    event_type: WebhookEventType
    
    model_config = {
        "from_attributes": True
    }

class WebhookCreate(WebhookBase):
    """Schema for creating webhooks"""
    secret_key: Optional[str] = None

class WebhookUpdate(BaseModel):
    """Schema for updating webhooks"""
    name: Optional[str] = None
    endpoint_url: Optional[HttpUrl] = None
    event_type: Optional[WebhookEventType] = None
    secret_key: Optional[str] = None
    is_active: Optional[bool] = None

class WebhookRead(WebhookBase):
    """Schema for reading webhooks"""
    id: str
    is_active: bool
    created_at: datetime
    last_triggered_at: Optional[datetime] = None
    
    model_config = {
        "from_attributes": True
    }

class WebhookList(BaseModel):
    """Schema for listing webhooks"""
    items: List[WebhookRead]
    total: int
    page: int
    page_size: int
