from datetime import datetime
from typing import Dict, Any, Optional, List
from uuid import UUID
from pydantic import BaseModel, Field

from models.campaign_template import TemplateCategory, TemplateStatus

class CampaignTemplateBase(BaseModel):
    """Base class for campaign template schemas"""
    name: str
    description: Optional[str] = None
    category: TemplateCategory = TemplateCategory.INFORMATIONAL
    content: Dict[str, Any] = Field(default_factory=dict)

class CampaignTemplateCreate(CampaignTemplateBase):
    """Schema for creating a campaign template"""
    pass

class CampaignTemplateUpdate(BaseModel):
    """Schema for updating a campaign template"""
    name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[TemplateCategory] = None
    status: Optional[TemplateStatus] = None
    content: Optional[Dict[str, Any]] = None

class CampaignTemplateRead(CampaignTemplateBase):
    """Schema for reading campaign template data"""
    id: UUID
    status: TemplateStatus
    created_at: datetime
    updated_at: datetime
    created_by: Optional[UUID] = None
    
    model_config = {"from_attributes": True}  # Pydantic v2 for ORM conversion

class CampaignTemplateList(BaseModel):
    """Schema for listing campaign templates"""
    items: List[CampaignTemplateRead]
    total: int
