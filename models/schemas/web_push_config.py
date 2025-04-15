from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, validator
from uuid import UUID, uuid4
from datetime import datetime

class WebPushConfigBase(BaseModel):
    """Base schema for Web Push Configuration"""
    name: str
    description: Optional[str] = None
    vapid_public_key: Optional[str] = None
    vapid_private_key: Optional[str] = None
    vapid_subject: Optional[str] = None
    default_icon_url: Optional[str] = None
    default_badge_url: Optional[str] = None
    service_worker_path: Optional[str] = '/service-worker.js'
    service_worker_scope: Optional[str] = '/'
    prompt_strategy: Optional[str] = 'immediate'  # immediate, delayed, custom
    custom_prompt_options: Optional[Dict[str, Any]] = None
    default_vibrate_pattern: Optional[List[int]] = None
    default_require_interaction: Optional[bool] = False
    default_silent: Optional[bool] = False
    default_renotify: Optional[bool] = False
    is_default: bool = False
    is_active: bool = True
    
    @validator('vapid_public_key', 'vapid_private_key', pre=True)
    def validate_keys(cls, v):
        # Allow empty values but not empty strings
        if v == "":
            return None
        return v

class WebPushConfigCreate(WebPushConfigBase):
    """Schema for creating a new Web Push Configuration"""
    pass

class WebPushConfigUpdate(BaseModel):
    """Schema for updating a Web Push Configuration"""
    name: Optional[str] = None
    description: Optional[str] = None
    vapid_public_key: Optional[str] = None
    vapid_private_key: Optional[str] = None
    vapid_subject: Optional[str] = None
    default_icon_url: Optional[str] = None
    default_badge_url: Optional[str] = None
    service_worker_path: Optional[str] = None
    service_worker_scope: Optional[str] = None
    prompt_strategy: Optional[str] = None
    custom_prompt_options: Optional[Dict[str, Any]] = None
    default_vibrate_pattern: Optional[List[int]] = None
    default_require_interaction: Optional[bool] = None
    default_silent: Optional[bool] = None
    default_renotify: Optional[bool] = None
    is_default: Optional[bool] = None
    is_active: Optional[bool] = None

class WebPushConfig(WebPushConfigBase):
    """Schema for Web Push Configuration"""
    id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        orm_mode = True