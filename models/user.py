from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, EmailStr, Field

class UserStatus(str, Enum):
    """User status enumeration"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING = "pending"
    BLOCKED = "blocked"
    DELETED = "deleted"

class UserDeviceType(str, Enum):
    """User device types"""
    MOBILE = "mobile"
    DESKTOP = "desktop"
    TABLET = "tablet"
    OTHER = "other"

class User(BaseModel):
    """Base user model"""
    id: Optional[str] = None
    email: EmailStr
    username: str
    full_name: Optional[str] = None
    status: UserStatus = UserStatus.PENDING
    is_active: bool = True
    is_superuser: bool = False
    
    # Notification preferences
    notification_enabled: bool = True
    webpush_enabled: bool = True
    email_notification_enabled: bool = True
    quiet_hours_start: Optional[int] = None  # Hour in 24-hour format
    quiet_hours_end: Optional[int] = None
    
    # Device and subscription info
    subscription_info: Dict[str, Any] = Field(default_factory=dict)
    devices: List[Dict[str, Any]] = Field(default_factory=list)
    
    # User attributes
    timezone: Optional[str] = "UTC"
    language: Optional[str] = "en"
    custom_attributes: Dict[str, Any] = Field(default_factory=dict)
    
    # Tracking
    last_login: Optional[datetime] = None
    last_seen: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        orm_mode = True
