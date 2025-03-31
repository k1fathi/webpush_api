from sqlalchemy import Column, Integer, String, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base

class Webhook(Base):
    __tablename__ = 'webhooks'

    webhook_id = Column(Integer, primary_key=True, index=True)
    webpush_id = Column(Integer, ForeignKey('webpush.webpush_id'))
    event = Column(String, nullable=False)
    payload = Column(String)
    status = Column(String)
    sent_at = Column(DateTime)
    
    # Relationship
    webpush = relationship("WebPush", back_populates="webhooks")
