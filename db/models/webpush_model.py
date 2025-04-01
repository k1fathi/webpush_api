from .base_model import Base, TimestampMixin
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship

class WebPush(Base, TimestampMixin):
    __tablename__ = "webpush"
    
    webpush_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.user_id'))
    template_id = Column(Integer, ForeignKey('templates.template_id'))
    campaign_id = Column(Integer, ForeignKey('campaigns.campaign_id'))
    trigger_id = Column(Integer, ForeignKey('triggers.trigger_id'))
    title = Column(String(255), nullable=False)
    body = Column(String(1000), nullable=False)
    icon = Column(String(255))
    image = Column(String(255))
    deep_link = Column(String(255))
    data = Column(JSON)
    status = Column(String(50))  # sent, delivered, failed
    sent_at = Column(DateTime)
    delivered_at = Column(DateTime)
    clicked_at = Column(DateTime)
    
    # Relationships
    user = relationship("User", back_populates="webpushes")
    template = relationship("Template", back_populates="webpushes")
    campaign = relationship("Campaign", back_populates="webpushes")
    trigger = relationship("Trigger", back_populates="webpushes")
    analytics = relationship("Analytics", back_populates="webpush", uselist=False)
    webhooks = relationship("Webhook", back_populates="webpush")
