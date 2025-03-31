from sqlalchemy import Column, Integer, String, Float, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from .base import Base

class Analytics(Base):
    __tablename__ = 'analytics'

    analytics_id = Column(Integer, primary_key=True, index=True)
    webpush_id = Column(Integer, ForeignKey('webpush.webpush_id'))
    delivered = Column(Boolean, default=False)
    clicked = Column(Boolean, default=False)
    delivery_status = Column(String)
    open_rate = Column(Float)
    click_rate = Column(Float)
    conversion_rate = Column(Float)
    
    # Relationship
    webpush = relationship("WebPush", back_populates="analytics")
