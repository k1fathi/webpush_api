import uuid
from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field

class WinningCriteria(str, Enum):
    OPEN_RATE = "open_rate"
    CLICK_RATE = "click_rate"
    CONVERSION = "conversion"
    ENGAGEMENT = "engagement"

class AbTest(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    campaign_id: str
    name: str
    description: Optional[str] = None
    variant_count: int
    winning_criteria: WinningCriteria = WinningCriteria.CLICK_RATE
    start_date: datetime = Field(default_factory=datetime.now)
    end_date: Optional[datetime] = None
    
    model_config = {"from_attributes": True}  # Updated from orm_mode for Pydantic v2
