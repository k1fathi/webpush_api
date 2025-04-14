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


class SubscriptionBase(BaseModel):
    """Base subscription schema"""
    endpoint: str
    p256dh: str
    auth: str


class SubscriptionCreate(SubscriptionBase):
    """Schema for creating a subscription"""
    user_id: Optional[UUID] = None


class SubscriptionUpdate(BaseModel):
    """Schema for updating a subscription"""
    endpoint: Optional[str] = None
    p256dh: Optional[str] = None
    auth: Optional[str] = None
    is_active: Optional[bool] = None


class SubscriptionRead(SubscriptionBase):
    """Schema for reading a subscription"""
    id: UUID
    user_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    last_notified_at: Optional[datetime] = None
    is_active: bool

    class Config:
        orm_mode = True


class SubscriptionList(BaseModel):
    """Schema for subscription list with pagination"""
    items: List[SubscriptionRead]
    total: int
    page: int
    page_size: int
