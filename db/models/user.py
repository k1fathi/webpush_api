from .base import Base, TimestampMixin
from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey
from sqlalchemy.orm import relationship

class User(Base, TimestampMixin):
    __tablename__ = "users"
    
    user_id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    segment = Column(String)
    last_login = Column(DateTime)
    birthday = Column(Date)
    membership_date = Column(Date)
    
    # Relationships
    webpushes = relationship("WebPush", back_populates="user")
    cdp_data = relationship("CDP", back_populates="user")
    cep_data = relationship("CEP", back_populates="user")
    segments = relationship("Segment", secondary="user_segments")
