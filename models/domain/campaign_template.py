from datetime import datetime
from typing import Dict, Any, Optional
from uuid import UUID

from sqlalchemy import Column, String, DateTime, Enum, JSON, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID as PgUUID

from db.base_class import Base
# Update the import to use models.schemas instead of models
from models.schemas.campaign_template import TemplateCategory, TemplateStatus

class CampaignTemplateModel(Base):
    """ORM model for campaign templates"""
    __tablename__ = "campaign_templates"
    
    id = Column(PgUUID(as_uuid=True), primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    description = Column(String, nullable=True)
    category = Column(Enum(TemplateCategory), default=TemplateCategory.INFORMATIONAL)
    status = Column(Enum(TemplateStatus), default=TemplateStatus.DRAFT)
    content = Column(JSON, nullable=False, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(PgUUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    
    # Relationship with user who created the template
    creator = relationship("UserModel", back_populates="created_templates")
    
    # Relationship with campaigns using this template
    campaigns = relationship("CampaignModel", back_populates="template")
