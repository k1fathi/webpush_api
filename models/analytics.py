import uuid
from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field

class ConversionType(str, Enum):
    PURCHASE = "purchase"
    SIGNUP = "signup"
    PAGEVIEW = "pageview"
    DOWNLOAD = "download"
    CUSTOM = "custom"

class Analytics(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    notification_id: str
    campaign_id: str
    user_id: str
    delivered: bool = False
    opened: bool = False
    clicked: bool = False
    event_time: datetime = Field(default_factory=datetime.now)
    user_action: Optional[str] = None
    conversion_type: Optional[ConversionType] = None
    conversion_value: float = 0.0
    
    model_config = {"from_attributes": True}  # Updated from orm_mode for Pydantic v2
