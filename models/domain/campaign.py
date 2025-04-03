import uuid
from datetime import datetime
from sqlalchemy import Boolean, Column, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, ENUM

from db.base_class import Base
from models.campaign import CampaignStatus, CampaignType

class CampaignModel(Base):
    """Campaign model for storing campaign data"""
    __tablename__ = "campaigns"

    # Ensure id is UUID type to match foreign keys in other tables
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    
    # Scheduling and status
    scheduled_time = Column(DateTime, nullable=True)
    status = Column(
        ENUM(CampaignStatus, name="campaign_status_enum", create_type=False),
        default=CampaignStatus.DRAFT
    )
    
    # Recurrence
    is_recurring = Column(Boolean, default=False)
    recurrence_pattern = Column(String, nullable=True)
    
    # Type of campaign
    campaign_type = Column(
        ENUM(CampaignType, name="campaign_type_enum", create_type=False),
        default=CampaignType.ONE_TIME
    )
    
    # Foreign keys - ensure these are UUID type too
    segment_id = Column(UUID(as_uuid=True), ForeignKey("segments.id"), nullable=True)
    template_id = Column(UUID(as_uuid=True), ForeignKey("templates.id"), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    segment = relationship("SegmentModel")
    template = relationship("TemplateModel")
    notifications = relationship("NotificationModel", back_populates="campaign")
    ab_tests = relationship("AbTestModel", back_populates="campaign")
    analytics = relationship("AnalyticsModel", back_populates="campaign")
    cep_decisions = relationship("CepDecisionModel", back_populates="campaign")
