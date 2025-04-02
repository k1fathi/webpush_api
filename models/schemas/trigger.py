from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field

from models.trigger import (
    TriggerType, TriggerStatus, TriggerAction, TriggerRule,
    ScheduleConfig, ActionConfig
)

class TriggerBase(BaseModel):
    """Base schema for triggers"""
    name: str
    description: Optional[str] = None
    trigger_type: TriggerType
    enabled: bool = True

class TriggerCreate(TriggerBase):
    """Schema for creating triggers"""
    rules: List[TriggerRule]
    schedule: Optional[ScheduleConfig] = None
    action: ActionConfig
    cooldown_period: Optional[int] = None  # in seconds
    max_triggers_per_day: Optional[int] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

class TriggerUpdate(BaseModel):
    """Schema for updating triggers"""
    name: Optional[str] = None
    description: Optional[str] = None
    rules: Optional[List[TriggerRule]] = None
    schedule: Optional[ScheduleConfig] = None
    action: Optional[ActionConfig] = None
    enabled: Optional[bool] = None
    cooldown_period: Optional[int] = None
    max_triggers_per_day: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = None

class TriggerRead(TriggerBase):
    """Schema for reading triggers"""
    id: str
    rules: List[TriggerRule]
    schedule: Optional[ScheduleConfig]
    action: ActionConfig
    status: TriggerStatus
    created_at: datetime
    updated_at: datetime
    last_triggered_at: Optional[datetime]
    trigger_count: int
    error_count: int
    metadata: Dict[str, Any]
    cooldown_period: Optional[timedelta]
    max_triggers_per_day: Optional[int]
    
    class Config:
        orm_mode = True

class TriggerList(BaseModel):
    """Schema for listing triggers"""
    items: List[TriggerRead]
    total: int
    page: int
    page_size: int

class TriggerEvent(BaseModel):
    """Schema for trigger events"""
    event_type: str
    event_data: Dict[str, Any]
    timestamp: Optional[datetime] = None
    user_id: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

class TriggerResult(BaseModel):
    """Schema for trigger execution results"""
    trigger_id: str
    executed_at: datetime
    success: bool
    action_result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
