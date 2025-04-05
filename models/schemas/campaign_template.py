from datetime import datetime
from enum import Enum
from typing import Dict, Any, Optional, List
from uuid import UUID
from pydantic import BaseModel, Field

class TemplateCategory(str, Enum):
    """Categories for campaign templates"""
    PROMOTIONAL = "promotional"
    TRANSACTIONAL = "transactional"
    INFORMATIONAL = "informational"
    REMINDER = "reminder"
    SURVEY = "survey"
    
class TemplateStatus(str, Enum):
    """Status values for templates"""
    DRAFT = "draft"
    ACTIVE = "active"
    ARCHIVED = "archived"
    DEPRECATED = "deprecated"

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
    
    model_config = {"from_attributes": True}

class CampaignTemplateList(BaseModel):
    """Schema for listing campaign templates"""
    items: List[CampaignTemplateRead]
    total: int
