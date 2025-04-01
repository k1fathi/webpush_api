import uuid
from datetime import datetime
from typing import Dict, List, Optional, Set
from sqlalchemy import Boolean, Column, String, DateTime, Table, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID

from db.base_class import Base

# Association table for user-role relationship
user_role = Table(
    'user_role',
    Base.metadata,
    Column('user_id', UUID(as_uuid=True), ForeignKey('users.id'), primary_key=True),
    Column('role_id', UUID(as_uuid=True), ForeignKey('roles.id'), primary_key=True)
)

# Association table for user-segment relationship
user_segment = Table(
    'user_segment',
    Base.metadata,
    Column('user_id', UUID(as_uuid=True), ForeignKey('users.id'), primary_key=True),
    Column('segment_id', UUID(as_uuid=True), ForeignKey('segments.id'), primary_key=True)
)

class UserModel(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    hashed_password = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    
    # WebPush related fields
    browser = Column(String, nullable=True)
    device_info = Column(String, nullable=True)
    push_token = Column(String, nullable=True)
    opted_in = Column(Boolean, default=True)
    subscription_date = Column(DateTime, default=datetime.utcnow)
    last_activity = Column(DateTime, nullable=True)
    custom_attributes = Column(JSON, default=dict)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    roles = relationship("RoleModel", secondary=user_role, back_populates="users")
    segments = relationship("SegmentModel", secondary=user_segment, back_populates="users")
    notifications = relationship("NotificationModel", back_populates="user")
    analytics = relationship("AnalyticsModel", back_populates="user")
    cdp_integration = relationship("CdpIntegrationModel", back_populates="user", uselist=False)
    cep_decisions = relationship("CepDecisionModel", back_populates="user")

    @property
    def permission_names(self) -> Set[str]:
        result = set()
        for role in self.roles:
            for permission in role.permissions:
                result.add(permission.name)
        return result

    def has_permission(self, permission_name: str) -> bool:
        # System administrator has all permissions
        if self.is_superuser:
            return True
            
        # Check if permission exists in any of user's roles
        return permission_name in self.permission_names
    
    def has_role(self, role_name: str) -> bool:
        return any(role.name == role_name for role in self.roles)
