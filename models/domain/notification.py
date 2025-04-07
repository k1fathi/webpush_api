import uuid
from datetime import datetime
from typing import Dict, Any, Optional

from sqlalchemy import Column, String, DateTime, JSON, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, ENUM

from db.base_class import Base
from models.schemas.notification import DeliveryStatus, NotificationType

class NotificationModel(Base):
    """Notification model for database operations"""
    __tablename__ = "notifications"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    campaign_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    template_id = Column(UUID(as_uuid=True), nullable=True)
    
    title = Column(String, nullable=False)
    body = Column(String, nullable=False)
    image_url = Column(String, nullable=True)
    action_url = Column(String, nullable=True)
    
    variant_id = Column(UUID(as_uuid=True), nullable=True)
    personalized_data = Column(JSON, default=dict)
    
    delivery_status = Column(
        ENUM(DeliveryStatus, name="delivery_status_enum", create_type=False),
        default=DeliveryStatus.PENDING
    )
    notification_type = Column(
        ENUM(NotificationType, name="notification_type_enum", create_type=False),
        default=NotificationType.CAMPAIGN
    )
    
    sent_at = Column(DateTime, nullable=True)
    delivered_at = Column(DateTime, nullable=True)
    opened_at = Column(DateTime, nullable=True)
    clicked_at = Column(DateTime, nullable=True)
    
    device_info = Column(JSON, default=dict)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("UserModel", back_populates="notifications")
    
    def __repr__(self):
        return f"<Notification {self.id} - {self.title}>"
