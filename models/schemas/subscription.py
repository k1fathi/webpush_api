"""Schemas for subscription data"""
import enum
from datetime import datetime
from typing import Dict, Any, Optional, List
from uuid import UUID

from pydantic import BaseModel, Field


class SubscriptionBase(BaseModel):
    """Base schema for push notification subscriptions"""
    endpoint: str
    keys: Dict[str, str]
    user_agent: Optional[str] = None
    browser_name: Optional[str] = None
    browser_version: Optional[str] = None
    os_name: Optional[str] = None
    os_version: Optional[str] = None
    device_type: Optional[str] = None
    is_mobile: Optional[bool] = False
    screen_resolution: Optional[str] = None
    language: Optional[str] = None
    
    # Status flags
    is_active: bool = True
    permission_status: str = "granted"  # granted, denied, default
    
    # Optional fields
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)
    user_id: Optional[UUID] = None
    topic_preferences: Optional[Dict[str, bool]] = Field(default_factory=dict)


class SubscriptionCreate(SubscriptionBase):
    """Schema for creating a new subscription"""
    pass


class SubscriptionUpdate(BaseModel):
    """Schema for updating a subscription"""
    endpoint: Optional[str] = None
    keys: Optional[Dict[str, str]] = None
    is_active: Optional[bool] = None
    permission_status: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    user_id: Optional[UUID] = None
    topic_preferences: Optional[Dict[str, bool]] = None
    last_used_at: Optional[datetime] = None


class SubscriptionRead(SubscriptionBase):
    """Schema for reading a subscription"""
    id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None
    last_used_at: Optional[datetime] = None
    last_notification_at: Optional[datetime] = None
    
    class Config:
        orm_mode = True


class SubscriptionStats(BaseModel):
    """Schema for subscription statistics"""
    total_subscriptions: int
    active_subscriptions: int
    inactive_subscriptions: int
    browser_distribution: Dict[str, int]
    os_distribution: Dict[str, int]
    device_distribution: Dict[str, int]
    daily_subscription_trend: Dict[str, int]
    weekly_subscription_trend: Dict[str, int]
    monthly_subscription_trend: Dict[str, int]


class SubscriptionFilter(BaseModel):
    """Filter parameters for subscription queries"""
    is_active: Optional[bool] = None
    browser_name: Optional[str] = None
    os_name: Optional[str] = None
    device_type: Optional[str] = None
    is_mobile: Optional[bool] = None
    user_id: Optional[UUID] = None
    created_after: Optional[datetime] = None
    created_before: Optional[datetime] = None
    last_used_after: Optional[datetime] = None
    topic: Optional[str] = None
