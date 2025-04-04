from typing import Dict, List, Optional, Set
from sqlalchemy.orm import Session
from fastapi import Depends

from db.session import get_session
from repositories.permission import PermissionRepository
from repositories.role import RoleRepository
from repositories.user import UserRepository

class PermissionService:
    """Service for managing permissions and roles"""
    
    def __init__(
        self,
        session: Session = Depends(get_session),
    ):
        """Initialize with repositories"""
        self.permission_repo = PermissionRepository(session)
        self.role_repo = RoleRepository(session)
        self.user_repo = UserRepository(session)
    
    async def user_has_permission(self, user_id: str, permission_name: str) -> bool:
        """
        Check if a user has a specific permission.
        This can be either through direct permission assignment or through roles.
        """
        # Find user's roles
        user_roles = await self.user_repo.get_user_roles(user_id)
        if not user_roles:
            return False
        
        # Check if any of the user's roles have the required permission
        for role_id in user_roles:
            role_permissions = await self.role_repo.get_role_permissions(role_id)
            if permission_name in role_permissions:
                return True
        
        # If we get here, no role had the required permission
        return False
    
    async def user_has_role(self, user_id: str, role_name: str) -> bool:
        """Check if a user has a specific role"""
        user_roles = await self.user_repo.get_user_role_names(user_id)
        return role_name in user_roles
    
    async def get_user_permissions(self, user_id: str) -> Set[str]:
        """Get all permissions for a user"""
        # Get all user's roles
        user_roles = await self.user_repo.get_user_roles(user_id)
        
        # Get permissions for each role
        all_permissions = set()
        for role_id in user_roles:
            role_permissions = await self.role_repo.get_role_permissions(role_id)
            if role_permissions:
                all_permissions.update(role_permissions)
        
        return all_permissions
    
    async def get_all_permissions(self, skip: int = 0, limit: int = 100, category: Optional[str] = None) -> List[Dict]:
        """Get all permissions with pagination and optional filtering"""
        permissions = await self.permission_repo.get_all()
        
        # Filter by category if provided
        if category:
            permissions = [p for p in permissions if p.category == category]
            
        # Apply pagination
        paginated = permissions[skip:skip+limit]
        
        return paginated
    
    async def get_permission(self, name: str) -> Optional[Dict]:
        """Get a permission by name"""
        return await self.permission_repo.get_by_name(name)
    
    async def get_permissions_by_role_name(self, role_name: str) -> List[str]:
        """Get all permissions for a role by name"""
        # Get role ID first
        role = await self.role_repo.get_by_name(role_name)
        if not role:
            return []
            
        # Then get permissions for that role
        permissions = await self.role_repo.get_role_permissions(str(role.id))
        return list(permissions)
