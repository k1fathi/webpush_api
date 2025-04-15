import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, Text, ForeignKey, JSON, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, ENUM, ARRAY, JSONB

from db.base_class import Base
from models.schemas.template import TemplateType, TemplateStatus

class TemplateModel(Base):
    """Template model for storing notification templates"""
    __tablename__ = "templates"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    
    # Template content
    title = Column(String, nullable=False)
    body = Column(Text, nullable=False)
    image_url = Column(String, nullable=True)
    action_url = Column(String, nullable=True)
    icon_url = Column(String, nullable=True)
    badge_url = Column(String, nullable=True)  # Badge shown when notification is collapsed
    
    # Web Push specific configuration
    vibrate = Column(JSONB, nullable=True)     # Vibration pattern for mobile devices
    require_interaction = Column(Boolean, default=False)  # Require user interaction to dismiss
    silent = Column(Boolean, default=False)    # Whether notification should be silent
    renotify = Column(Boolean, default=False)  # Whether to notify user again for a new notification
    time_to_live = Column(Integer, nullable=True)  # How long to keep trying to deliver (seconds)
    priority = Column(Integer, default=0)      # Priority of the notification (0 = normal, 2 = high)
    
    # Action buttons configuration
    actions = Column(JSONB, nullable=True)     # Action buttons for the notification
    
    # Template metadata
    template_type = Column(
        ENUM(TemplateType, name="template_type_enum", create_type=False),
        default=TemplateType.WEBPUSH
    )
    content = Column(JSON, default=dict)
    variables = Column(ARRAY(String), default=list)
    tags = Column(ARRAY(String), default=list)
    category = Column(String, nullable=True)
    
    # Status tracking
    status = Column(
        ENUM(TemplateStatus, name="template_status_enum", create_type=False),
        default=TemplateStatus.DRAFT
    )
    version = Column(Integer, default=1)
    
    # Timestamps and user tracking
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    
    # Relationships
    user = relationship("UserModel")
    versions = relationship("TemplateVersionModel", back_populates="template")
    campaigns = relationship("CampaignModel", back_populates="template")
    test_variants = relationship("TestVariantModel", back_populates="template")

class TemplateVersionModel(Base):
    """Template version model for storing version history"""
    __tablename__ = "template_versions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    template_id = Column(UUID(as_uuid=True), ForeignKey("templates.id"), nullable=False)
    version = Column(Integer, nullable=False)
    
    # Version content
    title = Column(String, nullable=False)
    body = Column(Text, nullable=False)
    image_url = Column(String, nullable=True)
    action_url = Column(String, nullable=True)
    icon_url = Column(String, nullable=True)
    badge_url = Column(String, nullable=True)  # Badge shown when notification is collapsed
    
    # Web Push specific configuration
    vibrate = Column(JSONB, nullable=True)
    require_interaction = Column(Boolean, nullable=True)
    silent = Column(Boolean, nullable=True)
    renotify = Column(Boolean, nullable=True)
    time_to_live = Column(Integer, nullable=True)
    priority = Column(Integer, nullable=True)
    
    # Action buttons configuration
    actions = Column(JSONB, nullable=True)
    
    content = Column(JSON, default=dict)
    
    # Timestamps and user tracking
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    
    # Relationships
    template = relationship("TemplateModel", back_populates="versions")
    user = relationship("UserModel")
