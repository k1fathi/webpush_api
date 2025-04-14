"""
Notification model for storing notification data.
"""

import uuid
from datetime import datetime
from typing import List, Optional

from sqlalchemy import Column, String, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from db.base_class import Base

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
    
    def __repr__(self):
        return f"<Notification {self.id}: {self.title}>"
