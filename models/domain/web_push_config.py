import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import Column, String, DateTime, Boolean, Integer, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from db.base_class import Base

class WebPushConfigModel(Base):
    """
    Web Push Configuration model for managing global web push notification settings.
    
    This model stores configuration settings for web push notifications, including
    default values, appearance settings, and behavior settings.
    """
    __tablename__ = "web_push_configs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    # Default appearance settings
    default_icon_url = Column(String, nullable=True)
    default_badge_url = Column(String, nullable=True)
    default_image_url = Column(String, nullable=True)
    
    # Default behavior settings
    default_time_to_live = Column(Integer, default=86400)  # 24 hours in seconds
    default_vibrate_pattern = Column(JSONB, nullable=True)
    default_require_interaction = Column(Boolean, default=False)
    default_silent = Column(Boolean, default=False)
    default_renotify = Column(Boolean, default=False)
    default_priority = Column(Integer, default=0)  # 0 = normal, 2 = high
    
    # Permission settings
    prompt_strategy = Column(String(50), default="immediate")  # immediate, delayed, or custom
    prompt_delay_seconds = Column(Integer, default=0)  # Delay before showing permission prompt
    min_visits_before_prompt = Column(Integer, default=1)  # Min visits before showing prompt
    
    # Service worker settings
    service_worker_path = Column(String, default="/service-worker.js")
    service_worker_scope = Column(String, default="/")
    
    # VAPID details
    vapid_public_key = Column(String, nullable=True)
    vapid_private_key = Column(String, nullable=True)
    vapid_subject = Column(String, nullable=True)  # Usually a mailto: URL
    
    # Timestamps and user tracking
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    updated_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    
    # Status flag
    is_active = Column(Boolean, default=True)
    is_default = Column(Boolean, default=False)
    
    # UI customization
    custom_prompt_options = Column(JSONB, nullable=True)  # Custom UI for permission prompt
    custom_styles = Column(JSONB, nullable=True)  # Custom CSS styles
    
    # Relationships
    creator = relationship("UserModel", foreign_keys=[created_by])
    updater = relationship("UserModel", foreign_keys=[updated_by])
    
    def __repr__(self):
        return f"<WebPushConfig {self.id}: {self.name}>"