from sqlalchemy import Column, Integer, String, Float, ForeignKey
from db.database import Base

class Analytics(Base):
    __tablename__ = 'analytics'

    analytics_id = Column(Integer, primary_key=True, index=True)
    webpush_id = Column(Integer, ForeignKey('webpush.webpush_id'))
    delivery_status = Column(String)
    open_rate = Column(Float)
    click_rate = Column(Float)
    conversion_rate = Column(Float)
