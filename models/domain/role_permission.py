import uuid
from datetime import datetime
from typing import List, Optional

from sqlalchemy import Column, String, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from db.session import Base

class RolePermissionModel(Base):
    """Role permission association model for database operations"""
    __tablename__ = "role_permissions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    role_id = Column(UUID(as_uuid=True), ForeignKey("roles.id", ondelete="CASCADE"), nullable=False)
    permission_name = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    role = relationship("RoleModel", back_populates="permissions")

    def __repr__(self):
        return f"<RolePermission {self.role_id}:{self.permission_name}>"
