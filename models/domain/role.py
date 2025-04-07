import uuid
from datetime import datetime
from typing import List, Optional, Set
from sqlalchemy import Column, String, DateTime, Table, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, ARRAY

from db.base_class import Base

# Association table for role-permission relationship
role_permission = Table(
    'role_permission',
    Base.metadata,
    Column('role_id', UUID(as_uuid=True), ForeignKey('roles.id'), primary_key=True),
    Column('permission_name', String, primary_key=True)
)

class RoleModel(Base):
    __tablename__ = "roles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, unique=True, index=True, nullable=False)
    description = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Fix relationships to use the proper tables and avoid circular references
    permissions = relationship("PermissionModel", secondary=role_permission)
    users = relationship("UserModel", secondary="user_role", overlaps="roles,user")

    @property
    def permission_names(self) -> Set[str]:
        return {permission.name for permission in self.permissions}

    def has_permission(self, permission_name: str) -> bool:
        return permission_name in self.permission_names

    def __repr__(self):
        return f"<Role {self.name}>"
