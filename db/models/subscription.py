from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Index, func
from sqlalchemy.orm import relationship
from db.config import Base

class Subscription(Base):
    # ...existing code from core/models.py Subscription class...
