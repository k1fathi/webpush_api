from sqlalchemy import Column, Integer, String, DateTime, JSON, Boolean, ForeignKey, Enum as SQLEnum, func, Index, Float
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
    targeting_rules = Column(JSON)  # country, last_activity, purchase_history
    webhooks = Column(JSON)  # delivery, click, conversion URLs
    user_id = Column(Integer, ForeignKey('users.id'))

    # Relationships
    schedule = relationship("NotificationSchedule", back_populates="notification", uselist=False)
    tracking = relationship("NotificationTracking", back_populates="notification", uselist=False)
    actions = relationship("NotificationAction", back_populates="notification")
    segments = relationship("NotificationSegment", back_populates="notification")
    campaign = relationship("Campaign", back_populates="notifications")
    template = relationship("Template")
    delivery_statuses = relationship("DeliveryStatus", back_populates="notification")
    webhook_events = relationship("WebhookEvent", back_populates="notification")
    data = relationship("NotificationData", back_populates="notification", uselist=False)
    cep_strategy = relationship("CEPStrategy", back_populates="notification", uselist=False)
    cdp_data = relationship("CDPData", back_populates="notification", uselist=False)
    user = relationship("User", back_populates="notifications")
    delivery_report = relationship("DeliveryReport", back_populates="notification", uselist=False)

class NotificationData(Base):
    __tablename__ = "notification_data"
    
    id = Column(Integer, primary_key=True)
    notification_id = Column(Integer, ForeignKey('notifications.id'))
    deep_link = Column(String)
    campaign_id = Column(String)
    variables = Column(JSON)  # name, product, time, link
    
    notification = relationship("Notification", back_populates="data")

class CEPStrategy(Base):
    __tablename__ = "cep_strategies"
    
    id = Column(Integer, primary_key=True)
    notification_id = Column(Integer, ForeignKey('notifications.id'))
    channel_priority = Column(JSON)  # Array of channels
    optimal_time = Column(String)
    
    notification = relationship("Notification", back_populates="cep_strategy")

class CDPData(Base):
    __tablename__ = "cdp_data"
    
    id = Column(Integer, primary_key=True)
    notification_id = Column(Integer, ForeignKey('notifications.id'))
    user_id = Column(String)
    profile = Column(JSON)  # loyalty_tier, last_purchase
    
    notification = relationship("Notification", back_populates="cdp_data")

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

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    name = Column(String)
    email = Column(String, unique=True)
    last_login = Column(DateTime)
    birthday = Column(DateTime, nullable=True)
    membership_date = Column(DateTime, default=datetime.utcnow)
    device_token = Column(String, nullable=True)
    is_subscribed = Column(Boolean, default=True)
    
    segments = relationship("UserSegment", back_populates="user")
    notifications = relationship("Notification", back_populates="user")
    cdp_profile = relationship("CDPProfile", back_populates="user", uselist=False)

class UserSegment(Base):
    __tablename__ = "user_segments"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    segment_id = Column(Integer, ForeignKey('segments.id'))
    
    user = relationship("User", back_populates="segments")
    segment = relationship("Segment", back_populates="users")

class Segment(Base):
    __tablename__ = "segments"
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String)
    criteria = Column(JSON)  # For segmentation rules

class DeliveryReport(Base):
    __tablename__ = "delivery_reports"
    
    id = Column(Integer, primary_key=True)
    notification_id = Column(Integer, ForeignKey('notifications.id'))
    delivered = Column(Boolean, default=False)
    delivered_time = Column(DateTime)
    open_rate = Column(Float, default=0.0)
    click_rate = Column(Float, default=0.0)
    
    notification = relationship("Notification", back_populates="delivery_report")
