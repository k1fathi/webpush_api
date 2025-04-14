from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PgUUID
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
    
    # Relationship
    user = relationship("UserModel", back_populates="subscriptions")
    
    def __repr__(self):
        return f"<Subscription {self.id}>"
