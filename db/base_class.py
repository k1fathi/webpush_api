from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, DateTime
from sqlalchemy.dialects.postgresql import UUID
import datetime
import uuid

# Create base class for all models
Base = declarative_base()

class BaseDBClass:
    """Base class for all ORM models with common fields and methods"""
    
    # Change to UUID type to ensure consistency across models
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    def __repr__(self):
        """String representation of the model"""
        return f"<{self.__class__.__name__}(id={self.id})>"
