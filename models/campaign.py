import uuid
from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field

class CampaignStatus(str, Enum):
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class CampaignType(str, Enum):
    ONE_TIME = "one_time"
    RECURRING = "recurring"
    TRIGGER_BASED = "trigger_based"
    AB_TEST = "ab_test"

class Campaign(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: Optional[str] = None
    scheduled_time: Optional[datetime] = None
    status: CampaignStatus = CampaignStatus.DRAFT
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    is_recurring: bool = False
    recurrence_pattern: Optional[str] = None
    campaign_type: CampaignType = CampaignType.ONE_TIME
    
    model_config = {"from_attributes": True}  # Updated from orm_mode for Pydantic v2
