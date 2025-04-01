from typing import List, Optional
from sqlalchemy import Column, String, Text
from sqlalchemy.orm import relationship

from db.base_class import Base

class PermissionModel(Base):
    __tablename__ = "permissions"

    name = Column(String, primary_key=True)
    description = Column(Text, nullable=True)
    
    # Relationships
    roles = relationship(
        "RoleModel",
        secondary="role_permission",
        back_populates="permissions",
    )
