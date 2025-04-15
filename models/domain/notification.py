"""
Notification model for storing notification data.
"""

import uuid
import enum
from datetime import datetime
from typing import List, Optional

from sqlalchemy import Column, String, DateTime, Boolean, Text, ForeignKey, Integer
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
    DISMISSED = "dismissed"  # Added for when user explicitly dismisses notification

class InteractionType(str, enum.Enum):
    """Enum for notification interaction types."""
    CLICK = "click"
    DISMISS = "dismiss"
    FOCUS = "focus"
    CLOSE = "close"

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
    
    # Web Push specific fields
    image_url = Column(String, nullable=True)  # Large image shown in notification
    icon_url = Column(String, nullable=True)   # Small icon shown in the notification
    badge_url = Column(String, nullable=True)  # Badge shown when notification is collapsed
    action_url = Column(String, nullable=True) # URL to open when notification is clicked
    vibrate = Column(JSONB, nullable=True)     # Vibration pattern for mobile devices
    priority = Column(Integer, default=0)      # Priority of the notification (0 = normal, 2 = high)
    time_to_live = Column(Integer, nullable=True)  # How long to keep trying to deliver
    renotify = Column(Boolean, default=False)  # Whether to notify user again for a new notification
    silent = Column(Boolean, default=False)    # Whether notification should be silent
    require_interaction = Column(Boolean, default=False)  # Whether notification requires user interaction to dismiss
    
    # Action buttons
    actions = Column(JSONB, nullable=True)     # Action buttons for the notification
    
    # Foreign keys
    campaign_id = Column(UUID(as_uuid=True), ForeignKey("campaigns.id"), nullable=True)
    variant_id = Column(UUID(as_uuid=True), ForeignKey("test_variants.id"), nullable=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    subscription_id = Column(UUID(as_uuid=True), ForeignKey("subscriptions.id"), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=True, onupdate=datetime.utcnow)
    scheduled_at = Column(DateTime, nullable=True)
    sent_at = Column(DateTime, nullable=True)
    delivered_at = Column(DateTime, nullable=True)
    interacted_at = Column(DateTime, nullable=True)
    
    # Status flags
    is_read = Column(Boolean, default=False)
    is_delivered = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    interaction_type = Column(String(50), nullable=True)  # Type of interaction (click, dismiss, etc.)
    
    # Delivery tracking
    delivery_attempts = Column(Integer, default=0)
    last_attempt_at = Column(DateTime, nullable=True)
    error_message = Column(Text, nullable=True)
    
    # Relationships - use string references to avoid circular imports
    # Analytics relationship - reverse side
    analytics = relationship("AnalyticsModel", back_populates="notification", cascade="all, delete-orphan")
    # Campaign relationship
    campaign = relationship("CampaignModel", back_populates="notifications")
    # Test variant relationship
    variant = relationship("TestVariantModel", back_populates="notifications")
    # User relationship
    user = relationship("UserModel", back_populates="notifications")
    # Subscription relationship
    subscription = relationship("SubscriptionModel")
    
    def __repr__(self):
        return f"<Notification {self.id}: {self.title}>"
