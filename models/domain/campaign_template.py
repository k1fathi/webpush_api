import uuid
from datetime import datetime
from typing import Dict, Any, Optional
from sqlalchemy import Column, String, DateTime, ForeignKey, JSON, Text
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, ENUM

from db.base_class import Base
from models.campaign_template import TemplateCategory, TemplateStatus

class CampaignTemplateModel(Base):
    """SQLAlchemy model for campaign templates"""
    __tablename__ = "campaign_templates"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    category = Column(ENUM(TemplateCategory), default=TemplateCategory.INFORMATIONAL)
    status = Column(ENUM(TemplateStatus), default=TemplateStatus.DRAFT)
    
    # Template content and structure
    content = Column(JSON, nullable=False)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    
    # Relationships
    creator = relationship("UserModel", back_populates="campaign_templates")
    campaigns = relationship("CampaignModel", back_populates="template")
