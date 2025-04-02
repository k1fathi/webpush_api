from datetime import datetime
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, EmailStr, Field, validator

from models.user import UserStatus, UserDeviceType

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
    
    class Config:
        orm_mode = True

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
