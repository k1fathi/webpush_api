from sqlalchemy import Column, Integer, String, ForeignKey, Table, Boolean, DateTime
from sqlalchemy.orm import relationship
from db.config import Base
from datetime import datetime

# Role-Permission Association Table
role_permissions = Table(
    'role_permissions',
    Base.metadata,
    Column('role_id', Integer, ForeignKey('roles.id')),
    Column('permission_id', Integer, ForeignKey('permissions.id'))
)

class Role(Base):
    __tablename__ = 'roles'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True)
    description = Column(String(200))
    permissions = relationship('Permission', secondary=role_permissions)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Pre-defined roles
    ADMIN = "ADMIN"
    TECH_ADMIN = "TECH_ADMIN"
    MARKETER = "MARKETER"
    ANALYST = "ANALYST"
    END_USER = "END_USER"

    @classmethod
    def get_default_permissions(cls, role_name):
        """Get default permissions for a role"""
        from core.permissions import DEFAULT_ROLE_PERMISSIONS
        return DEFAULT_ROLE_PERMISSIONS.get(role_name, [])

    def setup_default_permissions(self, db_session):
        """Set up default permissions for this role"""
        default_perms = self.get_default_permissions(self.name)
        for perm_name in default_perms:
            permission = db_session.query(Permission).filter_by(name=perm_name).first()
            if permission and permission not in self.permissions:
                self.permissions.append(permission)

class Permission(Base):
    __tablename__ = 'permissions'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True)
    description = Column(String(200))
    
    # Pre-defined permissions
    FULL_ACCESS = "full_access"
    CAMPAIGN_MANAGEMENT = "campaign_management"
    ANALYTICS_ACCESS = "analytics_access"
    SYSTEM_CONFIGURATION = "system_configuration"
    INTEGRATION_MANAGEMENT = "integration_management"

class UserActivity(Base):
    __tablename__ = 'user_activities'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    action = Column(String(100))
    module = Column(String(50))
    timestamp = Column(DateTime, default=datetime.utcnow)
    details = Column(String(500))
    status = Column(String(20))
    
    # Relationships
    user = relationship("User", back_populates="activities")
