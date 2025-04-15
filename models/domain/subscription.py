from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, JSON, Integer, Text
from sqlalchemy.dialects.postgresql import UUID as PgUUID, JSONB
from sqlalchemy.orm import relationship

from db.base_class import Base

class SubscriptionModel(Base):
    """Subscription model for web push notifications"""
    __tablename__ = "subscriptions"
    
    id = Column(PgUUID(), primary_key=True, default=uuid4, index=True)
    user_id = Column(PgUUID(), ForeignKey("users.id"), nullable=True, index=True)
    endpoint = Column(String, nullable=False)
    p256dh = Column(String, nullable=False)
    auth = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    last_notified_at = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Additional browser and device information
    user_agent = Column(String, nullable=True)
    browser_name = Column(String(50), nullable=True)
    browser_version = Column(String(50), nullable=True)
    os_name = Column(String(50), nullable=True)
    os_version = Column(String(50), nullable=True)
    device_type = Column(String(50), nullable=True)
    screen_resolution = Column(String(50), nullable=True)
    
    # Subscription stats
    notification_count = Column(Integer, default=0)
    successful_delivery_count = Column(Integer, default=0)
    failed_delivery_count = Column(Integer, default=0)
    
    # Performance metrics
    average_delivery_time = Column(Integer, nullable=True)  # Average time in ms
    
    # Permission status tracking
    permission_status = Column(String(20), default="granted")
    permission_updated_at = Column(DateTime, nullable=True)
    
    # Subscription metadata
    subscription_context = Column(JSONB, nullable=True)  # Context of where subscription occurred
    referrer = Column(String, nullable=True)  # Referring URL when subscription was created
    
    # Preferences
    frequency_cap_daily = Column(Integer, default=-1)  # -1 means no limit
    quiet_hours_start = Column(Integer, nullable=True)
    quiet_hours_end = Column(Integer, nullable=True)
    preferred_topics = Column(JSONB, nullable=True)  # Topics the user has shown interest in
    
    # Relationship
    user = relationship("UserModel", back_populates="subscriptions")
    web_push_events = relationship("WebPushEventModel", back_populates="subscription")
    
    def __repr__(self):
        return f"<Subscription {self.id}>"
