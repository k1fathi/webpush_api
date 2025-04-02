from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, DateTime
import datetime
import uuid

# Create base class for all models
Base = declarative_base()

class BaseDBClass:
    """Base class for all ORM models with common fields and methods"""
    
    id = Column(String(36), primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    def __repr__(self):
        """String representation of the model"""
        return f"<{self.__class__.__name__}(id={self.id})>"
