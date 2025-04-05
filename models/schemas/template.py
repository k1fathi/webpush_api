from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field, HttpUrl, field_validator

class TemplateType(str, Enum):
    """Template type enumeration"""
    WEBPUSH = "webpush"
    EMAIL = "email"
    SMS = "sms"
    IN_APP = "in_app"
    MOBILE_PUSH = "mobile_push"

class TemplateStatus(str, Enum):
    """Template status enumeration"""
    DRAFT = "draft"
    ACTIVE = "active"
    ARCHIVED = "archived"
    DELETED = "deleted"

class Template(BaseModel):
    """Template model"""
    id: Optional[str] = None
    name: str
    description: Optional[str] = None
    title: str
    body: str
    image_url: Optional[HttpUrl] = None
    action_url: Optional[HttpUrl] = None
    icon_url: Optional[HttpUrl] = None
    template_type: TemplateType = TemplateType.WEBPUSH
    content: Dict[str, Any] = Field(default_factory=dict)
    variables: List[str] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)
    status: TemplateStatus = TemplateStatus.DRAFT
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    created_by: Optional[str] = None
    version: int = 1
    category: Optional[str] = None
    
    model_config = {"from_attributes": True}

class TemplateBase(BaseModel):
    """Base schema for templates"""
    name: str
    description: Optional[str] = None
    template_type: TemplateType = TemplateType.WEBPUSH
    content: Dict[str, Any] = Field(default_factory=dict)
    variables: List[str] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)

    model_config = {
        "from_attributes": True
    }

class TemplateCreate(TemplateBase):
    """Schema for creating templates"""
    title: str
    body: str
    image_url: Optional[HttpUrl] = None
    action_url: Optional[HttpUrl] = None
    icon_url: Optional[HttpUrl] = None
    category: Optional[str] = None

    @field_validator('variables')
    @classmethod
    def extract_variables(cls, v, info):
        """Extract variables from content if not provided"""
        if not v and 'content' in info.data:
            # Extract variables from content (placeholders like {variable})
            import re
            content_str = str(info.data['content'])
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
    
    model_config = {
        "from_attributes": True
    }

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
    
    model_config = {"from_attributes": True}
