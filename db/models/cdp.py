from sqlalchemy import Column, Integer, JSON, ForeignKey
from .base import Base

class CDP(Base):
    __tablename__ = 'cdp'

    cdp_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.user_id'))
    data = Column(JSON)
