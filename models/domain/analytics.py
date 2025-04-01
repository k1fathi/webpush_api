import uuid
from datetime import datetime
from sqlalchemy import Boolean, Column, String, Float, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, ENUM

from db.base_class import Base
from models.analytics import ConversionType

class AnalyticsModel(Base):
    """Analytics model for tracking notification events"""
    __tablename__ = "analytics"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    notification_id = Column(UUID(as_uuid=True), ForeignKey("notifications.id"), nullable=False)
    campaign_id = Column(UUID(as_uuid=True), ForeignKey("campaigns.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Event tracking flags
    delivered = Column(Boolean, default=False)
    opened = Column(Boolean, default=False)
    clicked = Column(Boolean, default=False)
    
    # Event details
    event_time = Column(DateTime, default=datetime.utcnow)
    user_action = Column(String, nullable=True)
    
    # Conversion tracking
    conversion_type = Column(
        ENUM(ConversionType, name="conversion_type_enum", create_type=False), 
        nullable=True
    )
    conversion_value = Column(Float, default=0.0)
    
    # Relationships
    notification = relationship("NotificationModel", back_populates="analytics")
    campaign = relationship("CampaignModel", back_populates="analytics")
    user = relationship("UserModel", back_populates="analytics")
