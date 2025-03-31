from .base import Base, TimestampMixin
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship

class WebPush(Base, TimestampMixin):
    __tablename__ = "webpushes"
    
    webpush_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.user_id'))
    template_id = Column(Integer, ForeignKey('templates.template_id'))
    message = Column(String)
    status = Column(String)  # pending, sent, delivered, failed
    sent_at = Column(DateTime)
    opened_at = Column(DateTime)
    clicked_at = Column(DateTime)
    
    # Relationships
    user = relationship("User", back_populates="webpushes")
    template = relationship("Template")
    campaign = relationship("Campaign", back_populates="webpushes")
    analytics = relationship("Analytics", back_populates="webpush")
    webhooks = relationship("Webhook", back_populates="webpush")
