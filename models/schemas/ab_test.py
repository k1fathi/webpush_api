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

class AbTestBase(BaseModel):
    """Base schema for A/B tests"""
    name: str
    description: Optional[str] = None
    variant_count: int = 2
    winning_criteria: WinningCriteria = WinningCriteria.CLICK_RATE
    
    model_config = {
        "from_attributes": True
    }

class AbTestCreate(AbTestBase):
    """Schema for creating A/B tests"""
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

class AbTestUpdate(BaseModel):
    """Schema for updating A/B tests"""
    name: Optional[str] = None
    description: Optional[str] = None
    variant_count: Optional[int] = None
    winning_criteria: Optional[WinningCriteria] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

class AbTestRead(AbTestBase):
    """Schema for reading A/B tests"""
    id: str
    campaign_id: str
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    
    model_config = {
        "from_attributes": True
    }
