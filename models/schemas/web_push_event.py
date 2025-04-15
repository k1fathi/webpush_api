from datetime import datetime
from typing import Optional, Dict, Any, List
from uuid import UUID
from pydantic import BaseModel, Field


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
    pass


class WebPushEventRead(WebPushEventBase):
    """Schema for reading a web push event"""
    id: UUID
    created_at: datetime
    user_id: Optional[UUID] = None
    
    class Config:
        orm_mode = True


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