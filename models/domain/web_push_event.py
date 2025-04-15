import uuid
import enum
from datetime import datetime
from typing import Optional

from sqlalchemy import Column, String, DateTime, Integer, ForeignKey, Float, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from db.base_class import Base

class InteractionEventType(str, enum.Enum):
    """Enum for web push notification interaction event types."""
    RECEIVED = "received"          # Notification was received by the browser
    SHOWN = "shown"                # Notification was shown to the user
    CLICKED = "clicked"            # User clicked on the notification
    CLOSED = "closed"              # User closed the notification
    DISMISSED = "dismissed"        # User dismissed the notification
    ACTION_BUTTON = "action_button" # User clicked an action button
    FOCUS = "focus"                # Notification caused window to gain focus
    ERROR = "error"                # Error occurred with the notification
    PERMISSION_GRANTED = "permission_granted" # User granted permission
    PERMISSION_DENIED = "permission_denied"   # User denied permission
    SUBSCRIPTION_CHANGED = "subscription_changed" # Subscription details changed

class WebPushEventModel(Base):
    """
    Web Push Event model for tracking detailed interaction events with web push notifications.
    
    This model stores granular event data for web push notifications to enable
    detailed analysis of user interactions and behavior.
    """
    __tablename__ = "web_push_events"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Event type and data
    event_type = Column(String(50), nullable=False)
    event_data = Column(JSONB, nullable=True)     # Any data associated with the event
    event_timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # Foreign keys
    notification_id = Column(
        UUID(as_uuid=True), 
        ForeignKey("notifications.id", ondelete="CASCADE"),
        nullable=True
    )
    subscription_id = Column(
        UUID(as_uuid=True),
        ForeignKey("subscriptions.id", ondelete="SET NULL"),
        nullable=True
    )
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True
    )
    campaign_id = Column(
        UUID(as_uuid=True),
        ForeignKey("campaigns.id", ondelete="SET NULL"),
        nullable=True
    )
    
    # Context information
    page_url = Column(String, nullable=True)       # URL of the page when event occurred
    referrer = Column(String, nullable=True)       # Referrer URL
    action_id = Column(String, nullable=True)      # ID of action button if applicable
    
    # Device and browser information
    user_agent = Column(String, nullable=True)
    browser_name = Column(String(50), nullable=True)
    browser_version = Column(String(50), nullable=True)
    os_name = Column(String(50), nullable=True)
    os_version = Column(String(50), nullable=True)
    device_type = Column(String(50), nullable=True)
    screen_resolution = Column(String(50), nullable=True)
    
    # Location data
    ip_address = Column(String(50), nullable=True)
    country = Column(String(100), nullable=True)
    region = Column(String(100), nullable=True)
    city = Column(String(100), nullable=True)
    
    # Performance metrics
    time_since_sent = Column(Float, nullable=True)  # Time in seconds since notification was sent
    time_since_delivery = Column(Float, nullable=True)  # Time in seconds since delivered
    processing_time = Column(Float, nullable=True)  # Processing time in milliseconds
    
    # Error information
    error_message = Column(Text, nullable=True)
    error_code = Column(String(50), nullable=True)
    
    # Relationships
    notification = relationship("NotificationModel")
    subscription = relationship("SubscriptionModel", back_populates="web_push_events")
    user = relationship("UserModel", back_populates="web_push_events")
    campaign = relationship("CampaignModel")
    
    def __repr__(self):
        return f"<WebPushEvent {self.id}: {self.event_type}>"