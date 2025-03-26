from sqlalchemy import Column, Integer, String, DateTime, JSON, ForeignKey, func, Index
from sqlalchemy.orm import relationship
from core.database import Base

class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    body = Column(String, nullable=False)
    icon = Column(String, nullable=True)
    data = Column(JSON, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Index for faster querying
    __table_args__ = (
        Index('idx_notifications_created_at', 'created_at'),
    )

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
