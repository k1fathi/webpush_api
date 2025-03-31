from .base import Base, TimestampMixin
from sqlalchemy import Column, Integer, String, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship

class Campaign(Base, TimestampMixin):
    __tablename__ = "campaigns"
    
    campaign_id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime)
    status = Column(String)  # draft, active, completed, paused
    
    # Relationships
    webpushes = relationship("WebPush", back_populates="campaign")
    analytics = relationship("Analytics", back_populates="campaign")
