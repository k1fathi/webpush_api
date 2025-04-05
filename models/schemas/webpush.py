from datetime import datetime
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field, EmailStr, HttpUrl

class PushSubscriptionCreate(BaseModel):
    """Schema for creating a push subscription"""
    email: EmailStr
    subscription_json: str = Field(..., description="WebPush subscription object as JSON string")
    name: Optional[str] = None
    browser: Optional[str] = None
    device_info: Dict[str, Any] = Field(default_factory=dict)
    custom_attributes: Optional[Dict[str, Any]] = None
    
class PushSubscriptionUpdate(BaseModel):
    """Schema for updating a push subscription"""
    subscription_json: Optional[str] = None
    browser: Optional[str] = None
    device_info: Optional[Dict[str, Any]] = None
    custom_attributes: Optional[Dict[str, Any]] = None
    last_updated: datetime = Field(default_factory=datetime.utcnow)

class PushSubscriptionRead(BaseModel):
    """Schema for reading a push subscription"""
    user_id: str
    subscription_json: str
    browser: Optional[str] = None
    device_info: Dict[str, Any]
    created_at: datetime
    last_updated: Optional[datetime] = None
    
    model_config = {
        "from_attributes": True
    }

class VapidKeys(BaseModel):
    """Schema for VAPID keys"""
    public_key: str
    private_key: str

class WebPushNotification(BaseModel):
    """Schema for a web push notification"""
    title: str
    body: str
    icon: Optional[HttpUrl] = None
    image: Optional[HttpUrl] = None
    badge: Optional[HttpUrl] = None
    vibrate: Optional[List[int]] = None
    data: Dict[str, Any] = Field(default_factory=dict)
    actions: List[Dict[str, str]] = Field(default_factory=list)
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "title": "New Message",
                "body": "You have a new notification",
                "icon": "https://example.com/icon.png",
                "data": {"url": "https://example.com/details"},
                "actions": [
                    {"action": "view", "title": "View"},
                    {"action": "close", "title": "Dismiss"}
                ]
            }
        }
    }

class PushSubscriptionStats(BaseModel):
    """Schema for push subscription statistics"""
    total_subscriptions: int
    active_subscriptions: int
    browser_distribution: Dict[str, int]
    device_type_distribution: Dict[str, int]
    subscription_growth: List[Dict[str, Any]]
    
class PushSubscriptionsList(BaseModel):
    """Schema for listing push subscriptions"""
    items: List[PushSubscriptionRead]
    total: int
    page: int
    page_size: int
