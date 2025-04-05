import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, ENUM

from db.base_class import Base
from models.schemas.notification import DeliveryStatus

class NotificationModel(Base):
    """Notification model"""
    __tablename__ = "notifications"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    campaign_id = Column(UUID(as_uuid=True), ForeignKey("campaigns.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    template_id = Column(UUID(as_uuid=True), ForeignKey("templates.id"), nullable=False)
    
    title = Column(String, nullable=False)
    body = Column(Text, nullable=False)
    image_url = Column(String, nullable=True)
    action_url = Column(String, nullable=True)
    personalized_data = Column(JSON, default=dict)
    
    sent_at = Column(DateTime, nullable=True)
    delivery_status = Column(
        ENUM(DeliveryStatus, name="delivery_status_enum", create_type=False),
        default=DeliveryStatus.PENDING
    )
    delivered_at = Column(DateTime, nullable=True)
    opened_at = Column(DateTime, nullable=True)
    clicked_at = Column(DateTime, nullable=True)
    device_info = Column(JSON, default=dict)
    
    # New field to store variant ID for A/B testing
    variant_id = Column(UUID(as_uuid=True), ForeignKey("test_variants.id"), nullable=True)
    
    # Relationships
    campaign = relationship("CampaignModel", back_populates="notifications")
    user = relationship("UserModel", back_populates="notifications")
    template = relationship("TemplateModel")
    variant = relationship("TestVariantModel", back_populates="notifications")
    analytics = relationship("AnalyticsModel", back_populates="notification", uselist=False)
