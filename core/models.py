from sqlalchemy import Column, Integer, String, DateTime, JSON, Boolean, ForeignKey, Enum as SQLEnum, func, Index
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from core.database import Base

class NotificationPriority(enum.Enum):
    low = "low"
    medium = "medium"
    high = "high"

class NotificationType(enum.Enum):
    time_based = "time_based"
    trigger_based = "trigger_based"

class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    body = Column(String, nullable=False)
    icon = Column(String)
    image = Column(String)
    badge = Column(String)
    data = Column(JSON)
    priority = Column(SQLEnum(NotificationPriority))
    ttl = Column(Integer)
    require_interaction = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    variant_id = Column(String)
    ab_test_group = Column(String)
    campaign_id = Column(Integer, ForeignKey('campaigns.id'), nullable=True)
    template_id = Column(Integer, ForeignKey('templates.id'), nullable=True)

    # Relationships
    schedule = relationship("NotificationSchedule", back_populates="notification", uselist=False)
    tracking = relationship("NotificationTracking", back_populates="notification", uselist=False)
    actions = relationship("NotificationAction", back_populates="notification")
    segments = relationship("NotificationSegment", back_populates="notification")
    campaign = relationship("Campaign", back_populates="notifications")
    template = relationship("Template")
    delivery_statuses = relationship("DeliveryStatus", back_populates="notification")
    webhook_events = relationship("WebhookEvent", back_populates="notification")

class NotificationSchedule(Base):
    __tablename__ = "notification_schedules"

    id = Column(Integer, primary_key=True)
    notification_id = Column(Integer, ForeignKey('notifications.id'))
    type = Column(SQLEnum(NotificationType))
    trigger_type = Column(String)
    trigger_conditions = Column(JSON)
    send_at = Column(DateTime)
    
    notification = relationship("Notification", back_populates="schedule")

class NotificationAction(Base):
    __tablename__ = "notification_actions"

    id = Column(Integer, primary_key=True)
    notification_id = Column(Integer, ForeignKey('notifications.id'))
    type = Column(String)
    title = Column(String)
    action = Column(String)

    notification = relationship("Notification", back_populates="actions")

class NotificationTracking(Base):
    __tablename__ = "notification_tracking"

    id = Column(Integer, primary_key=True)
    notification_id = Column(Integer, ForeignKey('notifications.id'))
    enable_delivery_tracking = Column(Boolean, default=True)
    enable_open_tracking = Column(Boolean, default=True)
    enable_click_tracking = Column(Boolean, default=True)
    utm_params = Column(JSON)

    notification = relationship("Notification", back_populates="tracking")

class NotificationSegment(Base):
    __tablename__ = "notification_segments"

    id = Column(Integer, primary_key=True)
    notification_id = Column(Integer, ForeignKey('notifications.id'))
    segment_name = Column(String)
    targeting_rules = Column(JSON)

    notification = relationship("Notification", back_populates="segments")

class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True, index=True)
    endpoint = Column(String, nullable=False, unique=True)
    p256dh = Column(String, nullable=False)  # Public key for encryption
    auth = Column(String, nullable=False)    # Auth secret
    user_agent = Column(String, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    last_push_at = Column(DateTime, nullable=True)

    # Index for faster lookups
    __table_args__ = (
        Index('idx_subscriptions_endpoint', 'endpoint'),
    )

class Template(Base):
    __tablename__ = "templates"
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    title_template = Column(String, nullable=False)
    body_template = Column(String, nullable=False)
    variables = Column(JSON)  # ["name", "product", etc.]
    category = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

class CampaignSegment(Base):
    __tablename__ = "campaign_segments"

    id = Column(Integer, primary_key=True)
    campaign_id = Column(Integer, ForeignKey('campaigns.id'))
    segment_name = Column(String)

    campaign = relationship("Campaign", back_populates="campaign_segments")

class Campaign(Base):
    __tablename__ = "campaigns"
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    template_id = Column(Integer, ForeignKey('templates.id'))
    status = Column(String, nullable=True)  # draft, active, completed, paused
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=True)
    schedule_type = Column(String, nullable=False)  # immediate, scheduled, trigger-based
    trigger_conditions = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    template = relationship("Template")
    notifications = relationship("Notification", back_populates="campaign")
    campaign_segments = relationship("CampaignSegment", back_populates="campaign")

class DeliveryStatus(Base):
    __tablename__ = "delivery_statuses"
    
    id = Column(Integer, primary_key=True)
    notification_id = Column(Integer, ForeignKey('notifications.id'))
    subscription_id = Column(Integer, ForeignKey('subscriptions.id'))
    status = Column(String)  # sent, delivered, failed, clicked
    error = Column(String, nullable=True)
    delivered_at = Column(DateTime, nullable=True)
    clicked_at = Column(DateTime, nullable=True)
    
    notification = relationship("Notification")
    subscription = relationship("Subscription")

class WebhookEvent(Base):
    __tablename__ = "webhook_events"
    
    id = Column(Integer, primary_key=True)
    event_type = Column(String)  # delivery, click, conversion
    notification_id = Column(Integer, ForeignKey('notifications.id'))
    subscription_id = Column(Integer, ForeignKey('subscriptions.id'))
    payload = Column(JSON)
    processed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    notification = relationship("Notification")
    subscription = relationship("Subscription")
