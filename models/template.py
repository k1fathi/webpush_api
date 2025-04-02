from datetime import datetime
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field, HttpUrl

from models.schemas.template import TemplateType, TemplateStatus

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
    
    class Config:
        orm_mode = True
