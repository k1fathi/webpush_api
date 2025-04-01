from .base_model import Base, TimestampMixin
from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey, Table, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime

# Association tables
user_roles = Table(
    'user_roles', Base.metadata,
    Column('user_id', Integer, ForeignKey('users.user_id')),
    Column('role_id', Integer, ForeignKey('roles.id'))
)

user_segments = Table(
    'user_segments', Base.metadata,
    Column('user_id', Integer, ForeignKey('users.user_id')),
    Column('segment_id', Integer, ForeignKey('segments.segment_id'))
)

class User(Base, TimestampMixin):
    __tablename__ = "users"
    
    user_id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    email = Column(String(255), nullable=False, unique=True, index=True)
    password_hash = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    last_login = Column(DateTime)
    birthday = Column(Date)
    membership_date = Column(Date, default=datetime.utcnow)
    
    # Relationships from ERD
    roles = relationship("Role", secondary=user_roles, back_populates="users")
    segments = relationship("Segment", secondary=user_segments, back_populates="users")
    webpushes = relationship("WebPush", back_populates="user")
    cdp_data = relationship("CDP", back_populates="user")
    cep_data = relationship("CEP", back_populates="user")
    activities = relationship("UserActivity", back_populates="user")

    @property
    def is_admin(self):
        return any(role.name == "ADMIN" for role in self.roles)

    @property
    def permissions(self):
        all_permissions = set()
        for role in self.roles:
            all_permissions.update(perm.name for perm in role.permissions)
        return list(all_permissions)
