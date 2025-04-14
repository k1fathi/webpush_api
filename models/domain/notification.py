"""
Notification model for storing notification data.
"""

import uuid
import enum
from datetime import datetime
from typing import List, Optional

from sqlalchemy import Column, String, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from db.base_class import Base

class DeliveryStatus(str, enum.Enum):
    """Enum for notification delivery status."""
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"
    READ = "read"
    CLICKED = "clicked"

class NotificationModel(Base):
    """
    Notification model for storing notification data.
    
    This model represents a notification that can be sent to users through various channels.
    """
    __tablename__ = "notifications"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(255), nullable=False)
    body = Column(Text, nullable=True)
    data = Column(JSONB, nullable=True)
    status = Column(String(50), nullable=False, default="pending")
    type = Column(String(50), nullable=False, default="general")
    
    # Foreign keys
    campaign_id = Column(UUID(as_uuid=True), ForeignKey("campaigns.id"), nullable=True)
    variant_id = Column(UUID(as_uuid=True), ForeignKey("test_variants.id"), nullable=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=True, onupdate=datetime.utcnow)
    scheduled_at = Column(DateTime, nullable=True)
    sent_at = Column(DateTime, nullable=True)
    
    # Status flags
    is_read = Column(Boolean, default=False)
    is_delivered = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    
    # Relationships - use string references to avoid circular imports
    # Analytics relationship - reverse side
    analytics = relationship("AnalyticsModel", back_populates="notification", cascade="all, delete-orphan")
    # Campaign relationship
    campaign = relationship("CampaignModel", back_populates="notifications")
    # Test variant relationship
    variant = relationship("TestVariantModel", back_populates="notifications")
    # User relationship
    user = relationship("UserModel", back_populates="notifications")
    
    def __repr__(self):
        return f"<Notification {self.id}: {self.title}>"
