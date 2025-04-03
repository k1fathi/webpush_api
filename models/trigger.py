import uuid
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field

class TriggerEventType(str, Enum):
    CART_ABANDONMENT = "cart_abandonment"
    PRODUCT_VIEW = "product_view"
    BIRTHDAY = "birthday"
    SIGNUP_ANNIVERSARY = "signup_anniversary"
    INACTIVE_USER = "inactive_user"
    CUSTOM = "custom"

class TriggerType(str, Enum):
    """Types of triggers"""
    EVENT = "event"         # Triggered by specific events
    SCHEDULE = "schedule"   # Time-based triggers
    BEHAVIOR = "behavior"   # Based on user behavior/actions
    COMPOSITE = "composite" # Multiple conditions combined

class TriggerStatus(str, Enum):
    """Status of a trigger"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    PAUSED = "paused"
    ERROR = "error"

class TriggerAction(str, Enum):
    """Actions that can be taken when trigger fires"""
    SEND_NOTIFICATION = "send_notification"
    START_CAMPAIGN = "start_campaign"
    UPDATE_SEGMENT = "update_segment"
    WEBHOOK = "webhook"

class TriggerOperator(str, Enum):
    """Operators for combining multiple conditions"""
    AND = "and"
    OR = "or"
    NOT = "not"

class TriggerCondition(BaseModel):
    """Single condition for a trigger"""
    field: str
    operator: str
    value: Any
    metadata: Dict[str, Any] = Field(default_factory=dict)

class TriggerRule(BaseModel):
    """Rule containing one or more conditions"""
    conditions: List[TriggerCondition]
    operator: TriggerOperator = TriggerOperator.AND
    metadata: Dict[str, Any] = Field(default_factory=dict)

class ScheduleConfig(BaseModel):
    """Configuration for scheduled triggers"""
    frequency: str  # cron expression or frequency string
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    timezone: str = "UTC"
    blackout_periods: List[Dict[str, Any]] = Field(default_factory=list)

class ActionConfig(BaseModel):
    """Configuration for trigger actions"""
    action_type: TriggerAction
    template_id: Optional[str] = None
    campaign_id: Optional[str] = None
    segment_id: Optional[str] = None
    webhook_url: Optional[str] = None
    parameters: Dict[str, Any] = Field(default_factory=dict)

class Trigger(BaseModel):
    """Model representing a notification trigger"""
    id: Optional[str] = None
    name: str
    description: Optional[str] = None
    trigger_type: TriggerType
    status: TriggerStatus = TriggerStatus.ACTIVE
    
    # Trigger definition
    rules: List[TriggerRule] = Field(default_factory=list)
    schedule: Optional[ScheduleConfig] = None
    
    # Action to take when triggered
    action: ActionConfig
    
    # Metadata and tracking
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    last_triggered_at: Optional[datetime] = None
    trigger_count: int = 0
    error_count: int = 0
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    # Limits and thresholds
    cooldown_period: Optional[timedelta] = None
    max_triggers_per_day: Optional[int] = None
    enabled: bool = True
    
    model_config = {"from_attributes": True}  # Updated from orm_mode for Pydantic v2
