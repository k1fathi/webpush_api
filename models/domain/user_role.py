import uuid
from datetime import datetime
from typing import List, Optional

from sqlalchemy import Column, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from db.base_class import Base

class UserRoleModel(Base):
    """User role association model for database operations"""
    __tablename__ = "user_roles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    role_id = Column(UUID(as_uuid=True), ForeignKey("roles.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    role = relationship("RoleModel", back_populates="users")
    user = relationship("UserModel", back_populates="roles")

    def __repr__(self):
        return f"<UserRole {self.user_id}:{self.role_id}>"
