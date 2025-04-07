"""Schemas for subscription data"""
import enum
from datetime import datetime
from typing import Dict, Any, Optional, List
from uuid import UUID

from pydantic import BaseModel, Field, EmailStr


class SubscriptionStatus(str, enum.Enum):
    """Subscription status enum"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING = "pending"
    EXPIRED = "expired"
    REVOKED = "revoked"


class PushSubscriptionInfo(BaseModel):
    """Web Push Subscription object format"""
    endpoint: str = Field(..., description="Push subscription endpoint URL")
    keys: Dict[str, str] = Field(..., description="Encryption keys")
    expirationTime: Optional[int] = Field(None, description="Expiration timestamp (if any)")


class SubscriptionCreate(BaseModel):
    """Schema for creating a subscription"""
    subscription_info: PushSubscriptionInfo
    user_agent: Optional[str] = Field(None, description="Browser user agent")
    device_type: Optional[str] = Field(None, description="Device type")


class SubscriptionUpdate(BaseModel):
    """Schema for updating a subscription"""
    subscription_info: Optional[PushSubscriptionInfo] = None
    webpush_enabled: Optional[bool] = None
    status: Optional[SubscriptionStatus] = None


class SubscriptionRead(BaseModel):
    """Schema for reading a subscription"""
    id: UUID
    user_id: UUID
    email: EmailStr
    subscription_info: PushSubscriptionInfo
    webpush_enabled: bool
    status: SubscriptionStatus
    last_seen: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None


class SubscriptionStats(BaseModel):
    """Subscription statistics"""
    total_count: int
    active_count: int
    new_this_week: int
    lost_this_week: int
