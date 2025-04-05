from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, EmailStr, Field, field_validator, validator

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
        "from_attributes": True
    }

class UserBase(BaseModel):
    """Base schema for user data"""
    email: EmailStr
    username: str
    full_name: Optional[str] = None
    notification_enabled: bool = True
    webpush_enabled: bool = True
    email_notification_enabled: bool = True
    timezone: Optional[str] = "UTC"
    language: Optional[str] = "en"
    
    model_config = {
        "from_attributes": True
    }

class UserCreate(UserBase):
    """Schema for creating a user"""
    password: str
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        return v

class UserUpdate(BaseModel):
    """Schema for updating a user"""
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    full_name: Optional[str] = None
    password: Optional[str] = None
    notification_enabled: Optional[bool] = None
    webpush_enabled: Optional[bool] = None
    email_notification_enabled: Optional[bool] = None
    quiet_hours_start: Optional[int] = None
    quiet_hours_end: Optional[int] = None
    timezone: Optional[str] = None
    language: Optional[str] = None
    custom_attributes: Optional[Dict[str, Any]] = None

class UserRead(UserBase):
    """Schema for reading user data"""
    id: str
    status: UserStatus
    is_active: bool
    is_superuser: bool
    quiet_hours_start: Optional[int] = None
    quiet_hours_end: Optional[int] = None
    custom_attributes: Dict[str, Any]
    last_login: Optional[datetime] = None
    last_seen: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    model_config = {
        "from_attributes": True
    }

class UserList(BaseModel):
    """Schema for listing users"""
    items: List[UserRead]
    total: int
    page: int
    page_size: int

class UserDevice(BaseModel):
    """Schema for user device information"""
    device_id: str
    device_type: UserDeviceType
    name: Optional[str] = None
    platform: Optional[str] = None
    push_token: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_used: Optional[datetime] = None
    is_active: bool = True

class UserPreferences(BaseModel):
    """Schema for user preferences"""
    notification_enabled: bool = True
    webpush_enabled: bool = True
    email_notification_enabled: bool = True
    quiet_hours_start: Optional[int] = None
    quiet_hours_end: Optional[int] = None
    timezone: str = "UTC"
    language: str = "en"

class UserNotificationSettings(BaseModel):
    """Schema for user notification settings"""
    notification_enabled: bool
    webpush_enabled: bool
    email_notification_enabled: bool
    quiet_hours: Optional[Dict[str, int]] = None

class UserStats(BaseModel):
    """Schema for user statistics"""
    total_notifications: int
    open_rate: float
    click_rate: float
    last_interaction: Optional[datetime] = None
