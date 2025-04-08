"""Schemas for campaign data"""
import enum
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
from uuid import UUID

from pydantic import BaseModel, Field


class CampaignStatus(str, enum.Enum):
    """Campaign status enum"""
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    RUNNING = "running"
    COMPLETED = "completed"
    PAUSED = "paused"
    CANCELLED = "cancelled"


class CampaignType(str, enum.Enum):
    """Campaign type enum"""
    ONE_TIME = "one_time"
    RECURRING = "recurring"
    TRIGGERED = "triggered"


class Campaign(BaseModel):
    """Schema for campaign data"""
    id: Optional[str] = None
    name: str
    description: Optional[str] = None
    scheduled_time: Optional[datetime] = None
    status: CampaignStatus = CampaignStatus.DRAFT
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    is_recurring: bool = False
    recurrence_pattern: Optional[str] = None
    campaign_type: CampaignType = CampaignType.ONE_TIME
    segment_id: Optional[str] = None
    template_id: Optional[str] = None
    
    model_config = {"from_attributes": True}


class CampaignCreate(BaseModel):
    """Schema for creating a campaign"""
    name: str = Field(..., description="Campaign name")
    description: Optional[str] = Field(None, description="Campaign description")
    scheduled_time: Optional[datetime] = Field(None, description="Scheduled time")
    status: CampaignStatus = Field(CampaignStatus.DRAFT, description="Campaign status")
    is_recurring: bool = Field(False, description="Is the campaign recurring")
    recurrence_pattern: Optional[str] = Field(None, description="Recurrence pattern")
    campaign_type: CampaignType = Field(CampaignType.ONE_TIME, description="Campaign type")
    segment_id: Optional[UUID] = Field(None, description="Segment ID")
    template_id: Optional[UUID] = Field(None, description="Template ID")


class CampaignUpdate(BaseModel):
    """Schema for updating a campaign"""
    name: Optional[str] = Field(None, description="Campaign name")
    description: Optional[str] = Field(None, description="Campaign description")
    scheduled_time: Optional[datetime] = Field(None, description="Scheduled time")
    status: Optional[CampaignStatus] = Field(None, description="Campaign status")
    is_recurring: Optional[bool] = Field(None, description="Is the campaign recurring")
    recurrence_pattern: Optional[str] = Field(None, description="Recurrence pattern")
    campaign_type: Optional[CampaignType] = Field(None, description="Campaign type")
    segment_id: Optional[UUID] = Field(None, description="Segment ID")
    template_id: Optional[UUID] = Field(None, description="Template ID")


class CampaignRead(BaseModel):
    """Schema for reading a campaign"""
    id: UUID
    name: str
    description: Optional[str]
    scheduled_time: Optional[datetime]
    status: CampaignStatus
    is_recurring: bool
    recurrence_pattern: Optional[str]
    campaign_type: CampaignType
    segment_id: Optional[UUID]
    template_id: Optional[UUID]
    created_at: datetime
    updated_at: Optional[datetime]


class CampaignList(BaseModel):
    """Schema for listing campaigns with pagination"""
    items: List[CampaignRead]
    total: int
    page: int = 0
    page_size: int = 100


class CampaignPreview(BaseModel):
    """Schema for campaign preview"""
    id: Optional[UUID] = None
    name: str
    description: Optional[str] = None
    template: Dict[str, Any] = Field(default_factory=dict)
    segment_info: Optional[Dict[str, Any]] = None
    scheduled_time: Optional[datetime] = None
    status: CampaignStatus = CampaignStatus.DRAFT
    estimated_audience: Optional[int] = None
    personalization_example: Optional[Dict[str, Any]] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class CampaignValidation(BaseModel):
    """Schema for campaign validation"""
    is_valid: bool = True
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    segment_size: Optional[int] = None
    estimated_delivery_time: Optional[str] = None
    template_variables: Optional[List[str]] = None
    missing_variables: Optional[List[str]] = None
