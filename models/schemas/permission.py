from typing import Dict, List, Optional
from pydantic import BaseModel, Field

class PermissionBase(BaseModel):
    """Base schema for permissions"""
    name: str
    description: Optional[str] = None
    category: Optional[str] = None
    
    model_config = {
        "from_attributes": True
    }

class PermissionCreate(PermissionBase):
    """Schema for creating permissions"""
    pass

class PermissionUpdate(BaseModel):
    """Schema for updating permissions"""
    description: Optional[str] = None
    category: Optional[str] = None

class PermissionRead(PermissionBase):
    """Schema for reading permissions"""
    model_config = {
        "from_attributes": True
    }

class PermissionList(BaseModel):
    """Schema for listing permissions with pagination"""
    items: List[PermissionRead]
    total: int
    skip: int
    limit: int

class PermissionCheck(BaseModel):
    """Schema for checking if a user has a permission"""
    user_id: str
    permission_name: str
