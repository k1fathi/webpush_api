import uuid
from datetime import datetime
from typing import Dict, List, Optional, Set
from sqlalchemy import Boolean, Column, String, DateTime, Table, ForeignKey, JSON, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, ENUM, ARRAY
from sqlalchemy.sql import func

from db.base_class import Base
from models.schemas.user import UserStatus

# Association table for user-segment relationship
user_segment = Table(
    'user_segment',
    Base.metadata,
    Column('user_id', UUID(as_uuid=True), ForeignKey('users.id'), primary_key=True),
    Column('segment_id', UUID(as_uuid=True), ForeignKey('segments.id'), primary_key=True)
)

class UserModel(Base):
    """User model for database storage"""
    __tablename__ = "users"

    # Ensure id is UUID type to match foreign keys in other tables
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String)
    
    # User state
    status = Column(ENUM(UserStatus, name="user_status_enum", create_type=False), default=UserStatus.PENDING)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    
    # Notification preferences
    notification_enabled = Column(Boolean, default=True)
    webpush_enabled = Column(Boolean, default=True)
    email_notification_enabled = Column(Boolean, default=True)
    quiet_hours_start = Column(Integer, nullable=True)
    quiet_hours_end = Column(Integer, nullable=True)
    
    # Web push specific preferences
    webpush_permission_status = Column(String, nullable=True)  # granted, denied, default
    webpush_permission_updated_at = Column(DateTime, nullable=True)
    webpush_frequency_cap = Column(Integer, default=-1)  # -1 means no limit
    webpush_subscription_count = Column(Integer, default=0)
    
    # Device and subscription
    subscription_info = Column(JSON, default=dict)
    devices = Column(JSON, default=list)
    
    # User attributes
    timezone = Column(String, default="UTC")
    language = Column(String, default="en")
    custom_attributes = Column(JSON, default=dict)
    
    # Role and permissions
    role_id = Column(UUID(as_uuid=True), ForeignKey("roles.id"), nullable=True)
    permissions = Column(ARRAY(String), default=list)
    
    # Tracking
    last_login = Column(DateTime, nullable=True)
    last_seen = Column(DateTime, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Define relationship strings instead of direct imports to prevent circular imports
    role = relationship("RoleModel") # Direct role relationship
    roles = relationship("UserRoleModel", back_populates="user") # Changed to reference the model instead of the association table
    notifications = relationship("NotificationModel", back_populates="user")
    segments = relationship("SegmentModel", secondary=user_segment)
    cep_decisions = relationship("CepDecisionModel", back_populates="user")
    analytics = relationship("AnalyticsModel", back_populates="user")
    created_templates = relationship("CampaignTemplateModel", back_populates="creator", foreign_keys="CampaignTemplateModel.created_by")
    subscriptions = relationship("SubscriptionModel", back_populates="user")
    
    # New relationships for web push
    web_push_events = relationship("WebPushEventModel", back_populates="user")
    created_configs = relationship("WebPushConfigModel", foreign_keys="WebPushConfigModel.created_by", back_populates="creator")
    updated_configs = relationship("WebPushConfigModel", foreign_keys="WebPushConfigModel.updated_by", back_populates="updater")

    def __repr__(self):
        return f"<User {self.email}>"
