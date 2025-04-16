from datetime import datetime
from typing import Optional, Dict, Any, List
from uuid import UUID
from pydantic import BaseModel, Field
from enum import Enum


class InteractionEventType(str, Enum):
    """Enum for web push notification interaction event types"""
    DELIVERED = "delivered"
    CLICKED = "clicked"
    DISMISSED = "dismissed"
    FOCUS = "focus"
    CLOSE = "close"
    ERROR = "error"
    TIMEOUT = "timeout"
    RECEIVED = "received"


class WebPushEventBase(BaseModel):
    """Base schema for web push notification events"""
    event_type: str = Field(..., description="Type of event: delivered, clicked, dismissed, etc.")
    subscription_id: UUID = Field(..., description="ID of the subscription that received the event")
    notification_id: Optional[UUID] = Field(None, description="ID of the notification that triggered the event")
    campaign_id: Optional[UUID] = Field(None, description="ID of the campaign associated with the notification")
    
    # Event context data
    url: Optional[str] = Field(None, description="URL where the event occurred")
    interaction_data: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional interaction data")
    device_info: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Device information")
    
    # Performance metrics
    time_to_delivery_ms: Optional[int] = Field(None, description="Time from send to delivery in milliseconds")
    time_to_interaction_ms: Optional[int] = Field(None, description="Time from delivery to interaction in milliseconds")


class WebPushEventCreate(WebPushEventBase):
    """Schema for creating a new web push event"""
    user_id: Optional[UUID] = None
    event_data: Optional[Dict[str, Any]] = None
    page_url: Optional[str] = None
    referrer: Optional[str] = None
    action_id: Optional[str] = None
    user_agent: Optional[str] = None
    browser_name: Optional[str] = None
    browser_version: Optional[str] = None
    os_name: Optional[str] = None
    os_version: Optional[str] = None
    device_type: Optional[str] = None
    screen_resolution: Optional[str] = None
    ip_address: Optional[str] = None
    country: Optional[str] = None
    region: Optional[str] = None
    city: Optional[str] = None
    time_since_sent: Optional[int] = None
    time_since_delivery: Optional[int] = None
    processing_time: Optional[int] = None
    error_message: Optional[str] = None
    error_code: Optional[str] = None


class WebPushEvent(WebPushEventBase):
    """Schema for a web push event with full details"""
    id: UUID
    created_at: datetime
    user_id: Optional[UUID] = None
    event_data: Optional[Dict[str, Any]] = None
    page_url: Optional[str] = None
    referrer: Optional[str] = None
    action_id: Optional[str] = None
    user_agent: Optional[str] = None
    browser_name: Optional[str] = None
    browser_version: Optional[str] = None
    os_name: Optional[str] = None
    os_version: Optional[str] = None
    device_type: Optional[str] = None
    screen_resolution: Optional[str] = None
    ip_address: Optional[str] = None
    country: Optional[str] = None
    region: Optional[str] = None
    city: Optional[str] = None
    time_since_sent: Optional[int] = None
    time_since_delivery: Optional[int] = None
    processing_time: Optional[int] = None
    error_message: Optional[str] = None
    error_code: Optional[str] = None
    event_timestamp: Optional[datetime] = None
    
    class Config:
        from_attributes = True  # Updated from orm_mode for Pydantic v2 compatibility


class WebPushEventUpdate(BaseModel):
    """Schema for updating a web push event"""
    event_type: Optional[str] = None
    event_data: Optional[Dict[str, Any]] = None
    notification_id: Optional[UUID] = None
    subscription_id: Optional[UUID] = None
    user_id: Optional[UUID] = None
    campaign_id: Optional[UUID] = None
    page_url: Optional[str] = None
    referrer: Optional[str] = None
    action_id: Optional[str] = None
    user_agent: Optional[str] = None
    browser_name: Optional[str] = None
    browser_version: Optional[str] = None
    os_name: Optional[str] = None
    os_version: Optional[str] = None
    device_type: Optional[str] = None
    screen_resolution: Optional[str] = None
    ip_address: Optional[str] = None
    country: Optional[str] = None
    region: Optional[str] = None
    city: Optional[str] = None
    time_since_sent: Optional[int] = None
    time_since_delivery: Optional[int] = None
    processing_time: Optional[int] = None
    error_message: Optional[str] = None
    error_code: Optional[str] = None
    
    class Config:
        from_attributes = True  # Updated from orm_mode for Pydantic v2 compatibility


class WebPushEventRead(WebPushEventBase):
    """Schema for reading a web push event"""
    id: UUID
    created_at: datetime
    user_id: Optional[UUID] = None
    
    class Config:
        from_attributes = True  # Updated from orm_mode for Pydantic v2 compatibility


class WebPushEventStats(BaseModel):
    """Schema for web push event statistics"""
    total_events: int
    events_by_type: Dict[str, int]
    daily_events: Dict[str, Dict[str, int]]
    weekly_events: Dict[str, Dict[str, int]]
    monthly_events: Dict[str, Dict[str, int]]
    avg_time_to_delivery_ms: Optional[float] = None
    avg_time_to_interaction_ms: Optional[float] = None
    click_through_rate: Optional[float] = None
    dismiss_rate: Optional[float] = None
    conversion_rate: Optional[float] = None


class WebPushEventFilter(BaseModel):
    """Filter parameters for web push event queries"""
    event_type: Optional[str] = None
    subscription_id: Optional[UUID] = None
    notification_id: Optional[UUID] = None
    campaign_id: Optional[UUID] = None
    user_id: Optional[UUID] = None
    created_after: Optional[datetime] = None
    created_before: Optional[datetime] = None
