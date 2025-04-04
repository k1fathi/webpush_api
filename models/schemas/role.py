from datetime import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel, Field

class RoleBase(BaseModel):
    """Base schema for roles"""
    name: str
    description: Optional[str] = None
    
    model_config = {
        "from_attributes": True
    }

class RoleCreate(RoleBase):
    """Schema for creating roles"""
    permissions: Optional[List[str]] = None

class RoleUpdate(BaseModel):
    """Schema for updating roles"""
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None

class RoleRead(RoleBase):
    """Schema for reading roles"""
    id: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
    permission_names: List[str] = Field(default_factory=list)
    
    model_config = {
        "from_attributes": True
    }

class RoleList(BaseModel):
    """Schema for listing roles with pagination"""
    items: List[RoleRead]
    total: int
    skip: int
    limit: int

class RolePermissionsUpdate(BaseModel):
    """Schema for updating role permissions"""
    permissions: List[str]

class RoleUserAssignment(BaseModel):
    """Schema for assigning roles to users"""
    role_id: str
    user_id: str
