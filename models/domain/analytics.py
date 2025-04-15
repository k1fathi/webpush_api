import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import Column, String, DateTime, Boolean, Integer, ForeignKey, Float
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from db.base_class import Base

class AnalyticsModel(Base):
    """
    Analytics model for tracking notification metrics.
    
    This model stores analytics data related to notifications, including
    delivery status, open rates, click-through rates, and other metrics.
    """
    __tablename__ = "analytics"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Foreign key to notifications table
    notification_id = Column(
        UUID(as_uuid=True), 
        ForeignKey("notifications.id", ondelete="CASCADE"),
        nullable=False
    )
    
    # Foreign key to campaigns table
    campaign_id = Column(
        UUID(as_uuid=True),
        ForeignKey("campaigns.id", ondelete="SET NULL"),
        nullable=True
    )
    
    # Foreign key to users table
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True
    )
    
    # Foreign key to subscriptions table
    subscription_id = Column(
        UUID(as_uuid=True),
        ForeignKey("subscriptions.id", ondelete="SET NULL"),
        nullable=True
    )
    
    # Analytics data
    delivery_status = Column(String(50), nullable=False, default="pending")
    opened = Column(Boolean, default=False)
    clicked = Column(Boolean, default=False)
    dismissed = Column(Boolean, default=False)  # User explicitly dismissed notification
    open_count = Column(Integer, default=0)
    click_count = Column(Integer, default=0)
    dismiss_count = Column(Integer, default=0)
    
    # Web push specific metrics
    time_to_delivery = Column(Float, nullable=True)  # Time from send to delivery in seconds
    time_to_click = Column(Float, nullable=True)     # Time from delivery to click in seconds
    time_to_dismiss = Column(Float, nullable=True)   # Time from delivery to dismiss in seconds
    interaction_count = Column(Integer, default=0)   # Total number of interactions
    
    # Device and platform information
    device_type = Column(String(50), nullable=True)
    platform = Column(String(50), nullable=True)
    browser = Column(String(50), nullable=True)
    screen_size = Column(String(50), nullable=True)  # Format: "width x height"
    
    # Location data
    country = Column(String(100), nullable=True)
    region = Column(String(100), nullable=True)
    city = Column(String(100), nullable=True)
    ip_address = Column(String(50), nullable=True)
    
    # Additional metadata
    data_metadata = Column(JSONB, nullable=True)  # Renamed from metadata to data_metadata
    
    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=True, onupdate=datetime.utcnow)
    delivered_at = Column(DateTime, nullable=True)
    opened_at = Column(DateTime, nullable=True)
    clicked_at = Column(DateTime, nullable=True)
    dismissed_at = Column(DateTime, nullable=True)
    
    # Relationship to notifications table - use string reference to avoid circular imports
    notification = relationship("NotificationModel", back_populates="analytics")
    # Relationship to campaigns table
    campaign = relationship("CampaignModel", back_populates="analytics")
    # Relationship to users table
    user = relationship("UserModel", back_populates="analytics")
    # Relationship to subscriptions table
    subscription = relationship("SubscriptionModel")
    
    def __repr__(self):
        return f"<Analytics {self.id} for notification {self.notification_id}>"
