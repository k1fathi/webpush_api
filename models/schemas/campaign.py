from datetime import datetime
from typing import Dict, List, Optional, Union
from pydantic import BaseModel, Field, HttpUrl

from models.campaign import CampaignStatus, CampaignType

class CampaignBase(BaseModel):
    """Base schema for campaigns"""
    name: str
    description: Optional[str] = None
    campaign_type: CampaignType = CampaignType.ONE_TIME
    is_recurring: bool = False
    recurrence_pattern: Optional[str] = None
    
    model_config = {
        "from_attributes": True  # Updated from orm_mode = True
    }

class CampaignCreate(CampaignBase):
    """Schema for creating campaigns"""
    segment_id: Optional[str] = None
    template_id: Optional[str] = None
    scheduled_time: Optional[datetime] = None

class CampaignUpdate(BaseModel):
    """Schema for updating campaigns"""
    name: Optional[str] = None
    description: Optional[str] = None
    segment_id: Optional[str] = None
    template_id: Optional[str] = None
    scheduled_time: Optional[datetime] = None
    is_recurring: Optional[bool] = None
    recurrence_pattern: Optional[str] = None
    campaign_type: Optional[CampaignType] = None

class CampaignRead(CampaignBase):
    """Schema for reading campaigns"""
    id: str
    status: CampaignStatus
    created_at: datetime
    updated_at: datetime
    scheduled_time: Optional[datetime] = None
    segment_id: Optional[str] = None
    template_id: Optional[str] = None
    
    model_config = {
        "from_attributes": True
    }

class CampaignList(BaseModel):
    """Schema for listing campaigns with pagination"""
    items: List[CampaignRead]
    total: int
    skip: int
    limit: int

class CampaignPreview(BaseModel):
    """Schema for campaign preview"""
    title: str
    body: str
    image_url: Optional[HttpUrl] = None
    action_url: Optional[HttpUrl] = None
    campaign_id: str
    template_id: str
    personalized: bool

class CampaignValidation(BaseModel):
    """Schema for campaign validation result"""
    campaign_id: str
    is_valid: bool
    errors: List[str] = []
    warnings: List[str] = []

class ABTestCampaignCreate(BaseModel):
    """Schema for creating an A/B test campaign"""
    campaign: CampaignCreate
    ab_test: Dict
