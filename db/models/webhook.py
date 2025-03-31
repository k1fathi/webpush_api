from sqlalchemy import Column, Integer, String, DateTime, JSON
from db.database import Base

class Webhook(Base):
    __tablename__ = 'webhooks'

    webhook_id = Column(Integer, primary_key=True, index=True)
    event = Column(String, nullable=False)
    payload = Column(String)
    status = Column(String)
    sent_at = Column(DateTime)
