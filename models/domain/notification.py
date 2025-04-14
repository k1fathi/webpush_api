from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, JSON, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from core.db import Base

class DeliveryStatus(str, enum.Enum):
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"
    CLICKED = "clicked"

class NotificationModel(Base):
    __tablename__ = "notifications"
    
    id = Column(Integer, primary_key=True, index=True)
    subscription_id = Column(Integer, ForeignKey("subscriptions.id"), nullable=False)
    title = Column(String, nullable=False)
    body = Column(Text, nullable=True)
    icon = Column(String, nullable=True)
    badge = Column(String, nullable=True)
    image = Column(String, nullable=True)
    data = Column(JSON, nullable=True)
    actions = Column(JSON, nullable=True)
    tag = Column(String, nullable=True)
    silent = Column(Boolean, default=False)
    require_interaction = Column(Boolean, default=False)
    renotify = Column(Boolean, default=False)
    sent_at = Column(DateTime(timezone=True), server_default=func.now())
    delivered = Column(Boolean, default=False)
    delivered_at = Column(DateTime(timezone=True), nullable=True)
    
    subscription = relationship("SubscriptionModel", back_populates="notifications")
    
    def __repr__(self):
        return f"<Notification {self.id}: {self.title}>"
