import uuid
from datetime import datetime
from typing import List, Optional

from sqlalchemy import Column, String, Boolean, DateTime
from sqlalchemy.dialects.postgresql import UUID

from db.base_class import Base

class PermissionModel(Base):
    """Permission model for database operations"""
    __tablename__ = "permissions"

    name = Column(String, primary_key=True)
    description = Column(String, nullable=True)
    category = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Permission {self.name}>"
