from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from models.ab_test import WinningCriteria

class AbTestBase(BaseModel):
    """Base schema for A/B tests"""
    name: str
    description: Optional[str] = None
    variant_count: int = 2
    winning_criteria: WinningCriteria = WinningCriteria.CLICK_RATE

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
    
    class Config:
        orm_mode = True
