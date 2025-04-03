from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any
# Update imports for Pydantic v2
from pydantic import BaseModel, EmailStr, Field, field_validator

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

class UserSubscriptionStatus(str, Enum):
    SUBSCRIBED = "subscribed"
    UNSUBSCRIBED = "unsubscribed"
    PENDING = "pending"

class UserRole(str, Enum):
    USER = "user"
    ADMIN = "admin"
    MARKETER = "marketer"
    DEVELOPER = "developer"

class DeviceInfo(BaseModel):
    browser: Optional[str] = None
    browser_version: Optional[str] = None
    os: Optional[str] = None
    os_version: Optional[str] = None
    device_type: Optional[str] = None
    screen_size: Optional[str] = None

class User(BaseModel):
    """Base user model"""
    id: Optional[str] = Field(None, description="Unique identifier")
    email: Optional[str] = Field(None, description="User email")
    username: Optional[str] = Field(None, description="Username for login")
    first_name: Optional[str] = Field(None, description="First name")
    last_name: Optional[str] = Field(None, description="Last name")
    subscription_status: UserSubscriptionStatus = UserSubscriptionStatus.PENDING
    created_at: Optional[datetime] = Field(None, description="User creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")
    last_login: Optional[datetime] = Field(None, description="Last login timestamp")
    role: UserRole = UserRole.USER
    preferences: Dict[str, Any] = Field(default_factory=dict)
    device_info: Optional[DeviceInfo] = None
    push_token: Optional[str] = Field(None, description="WebPush subscription token")
    opted_in: bool = False
    is_active: bool = True
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "email": "user@example.com",
                "username": "johndoe",
                "first_name": "John",
                "last_name": "Doe",
                "subscription_status": "subscribed",
                "role": "user",
                "preferences": {"language": "en", "notifications": True},
                "opted_in": True
            }
        },
        "from_attributes": True  # Updated from orm_mode = True
    }
