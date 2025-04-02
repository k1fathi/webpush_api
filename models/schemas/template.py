from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field, HttpUrl, validator

class TemplateType(str, Enum):
    """Template types"""
    WEBPUSH = "webpush"
    EMAIL = "email"
    SMS = "sms"
    IN_APP = "in_app"

class TemplateStatus(str, Enum):
    """Template status"""
    DRAFT = "draft"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    REJECTED = "rejected"
    ARCHIVED = "archived"
    ACTIVE = "active"

class TemplateBase(BaseModel):
    """Base schema for templates"""
    name: str
    description: Optional[str] = None
    template_type: TemplateType = TemplateType.WEBPUSH
    content: Dict[str, Any] = Field(default_factory=dict)
    variables: List[str] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)

class TemplateCreate(TemplateBase):
    """Schema for creating templates"""
    title: str
    body: str
    image_url: Optional[HttpUrl] = None
    action_url: Optional[HttpUrl] = None
    icon_url: Optional[HttpUrl] = None
    category: Optional[str] = None

    @validator('variables')
    def extract_variables(cls, v, values):
        """Extract variables from content if not provided"""
        if not v and 'content' in values:
            # Extract variables from content (placeholders like {variable})
            import re
            content_str = str(values['content'])
            v = list(set(re.findall(r'\{([a-zA-Z0-9_]+)\}', content_str)))
        return v

class TemplateUpdate(BaseModel):
    """Schema for updating templates"""
    name: Optional[str] = None
    description: Optional[str] = None
    title: Optional[str] = None
    body: Optional[str] = None
    image_url: Optional[HttpUrl] = None
    action_url: Optional[HttpUrl] = None
    icon_url: Optional[HttpUrl] = None
    content: Optional[Dict[str, Any]] = None
    variables: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    category: Optional[str] = None
    status: Optional[TemplateStatus] = None

class TemplateRead(TemplateBase):
    """Schema for reading templates"""
    id: str
    title: str
    body: str
    image_url: Optional[HttpUrl] = None
    action_url: Optional[HttpUrl] = None
    icon_url: Optional[HttpUrl] = None
    created_at: datetime
    updated_at: datetime
    created_by: Optional[str] = None
    status: TemplateStatus
    version: int = 1
    category: Optional[str] = None
    
    class Config:
        orm_mode = True

class TemplateList(BaseModel):
    """Schema for listing templates with pagination"""
    items: List[TemplateRead]
    total: int
    skip: int
    limit: int

class TemplatePreview(BaseModel):
    """Schema for template preview"""
    title: str
    body: str
    image_url: Optional[HttpUrl] = None
    action_url: Optional[HttpUrl] = None
    icon_url: Optional[HttpUrl] = None
    rendered_content: Dict[str, Any] = Field(default_factory=dict)
    
class TemplateValidation(BaseModel):
    """Schema for template validation"""
    is_valid: bool
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)

class TemplateVersion(BaseModel):
    """Schema for template version"""
    id: str
    template_id: str
    version: int
    content: Dict[str, Any]
    created_at: datetime
    created_by: Optional[str] = None
    
    class Config:
        orm_mode = True
