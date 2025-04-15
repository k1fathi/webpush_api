import uuid
from datetime import datetime
from sqlalchemy import Boolean, Column, String, DateTime, Text, ForeignKey, Integer, Float, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, ENUM, JSONB

from db.base_class import Base
from models.schemas.campaign import CampaignStatus, CampaignType

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
    
    # Web Push specific settings
    delivery_policy = Column(JSONB, nullable=True)  # Rules for when to deliver notifications
    throttling_rate = Column(Integer, nullable=True)  # Notifications per minute
    audience_limit = Column(Integer, nullable=True)  # Max number of users to target
    
    # Web Push campaign metrics
    sent_count = Column(Integer, default=0)
    delivered_count = Column(Integer, default=0)
    clicked_count = Column(Integer, default=0)
    dismissed_count = Column(Integer, default=0)
    failed_count = Column(Integer, default=0)
    
    # Performance metrics
    click_rate = Column(Float, nullable=True)  # Clicked / Delivered
    dismiss_rate = Column(Float, nullable=True)  # Dismissed / Delivered
    conversion_rate = Column(Float, nullable=True)  # Conversions / Clicked
    
    # A/B testing configuration
    is_ab_test = Column(Boolean, default=False)
    ab_test_config = Column(JSONB, nullable=True)
    
    # Custom notification payload overrides
    custom_notification_options = Column(JSONB, nullable=True)
    
    # Foreign keys - ensure these are UUID type too
    segment_id = Column(UUID(as_uuid=True), ForeignKey("segments.id"), nullable=True)
    template_id = Column(UUID(as_uuid=True), ForeignKey("templates.id"), nullable=True)
    web_push_config_id = Column(UUID(as_uuid=True), ForeignKey("web_push_configs.id"), nullable=True)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    
    # Relationships
    segment = relationship("SegmentModel")
    template = relationship("TemplateModel", back_populates="campaigns")
    notifications = relationship("NotificationModel", back_populates="campaign")
    ab_tests = relationship("AbTestModel", back_populates="campaign")
    analytics = relationship("AnalyticsModel", back_populates="campaign")
    cep_decisions = relationship("CepDecisionModel", back_populates="campaign")
    web_push_config = relationship("WebPushConfigModel")
    creator = relationship("UserModel", foreign_keys=[created_by])
    web_push_events = relationship("WebPushEventModel")
    
    def __repr__(self):
        return f"<Campaign {self.id}: {self.name}>"
