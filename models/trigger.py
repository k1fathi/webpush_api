import uuid
from datetime import datetime
from enum import Enum
from typing import Dict, Optional
from pydantic import BaseModel, Field

class TriggerEventType(str, Enum):
    CART_ABANDONMENT = "cart_abandonment"
    PRODUCT_VIEW = "product_view"
    BIRTHDAY = "birthday"
    SIGNUP_ANNIVERSARY = "signup_anniversary"
    INACTIVE_USER = "inactive_user"
    CUSTOM = "custom"

class Trigger(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    event_type: TriggerEventType
    conditions: Dict = Field(default_factory=dict)
    template_id: str
    segment_id: Optional[str] = None
    delay_minutes: int = 0
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.now)
    
    class Config:
        orm_mode = True
