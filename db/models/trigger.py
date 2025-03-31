from sqlalchemy import Column, Integer, String
from db.database import Base

class Trigger(Base):
    __tablename__ = 'triggers'

    trigger_id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    condition = Column(String, nullable=False)
