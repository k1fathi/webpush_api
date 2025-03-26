from sqlalchemy import Column, Integer, String, ARRAY, DateTime, func, Index
from sqlalchemy.dialects.postgresql import JSONB
from database import Base

class Notification(Base):
    __tablename__ = "notifications"
    
    id = Column(Integer, primary_key=True, index=True)
    template = Column(JSONB)
    segments = Column(ARRAY(String))
    notification_metadata = Column(JSONB)
    created_at = Column(DateTime, server_default=func.now())

    # Create GIN indexes
    __table_args__ = (
        Index('ix_notifications_template_gin', template, postgresql_using='gin'),
        Index('ix_notifications_segments_gin', segments, postgresql_using='gin'),
        Index('ix_notifications_metadata_gin', notification_metadata, postgresql_using='gin'),
    )

class Subscription(Base):
    __tablename__ = "subscriptions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_data = Column(JSONB)
    segments = Column(ARRAY(String))
    status = Column(String)
    
    # Create GIN indexes
    __table_args__ = (
        Index('ix_subscriptions_user_data_gin', user_data, postgresql_using='gin'),
        Index('ix_subscriptions_segments_gin', segments, postgresql_using='gin'),
    )
