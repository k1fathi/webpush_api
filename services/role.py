from typing import Dict, List, Optional, Any

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from db.session import get_session
from models.domain.role import RoleModel
from models.schemas.role import RoleCreate, RoleUpdate
from repositories.role import RoleRepository
from repositories.user import UserRepository

class RoleService:
    """Service for managing roles"""
    
    def __init__(
        self,
        session: AsyncSession = Depends(get_session),
    ):
        """Initialize with session"""
        self.role_repo = RoleRepository(session)
        self.user_repo = UserRepository(session)
        
    async def create_role(self, role_data: RoleCreate) -> Dict[str, Any]:
        """Create a new role"""
        # Check if role with same name already exists
        existing_role = await self.role_repo.get_by_name(role_data.name)
        if existing_role:
            raise ValueError(f"Role with name '{role_data.name}' already exists")
            
        # Create role
        role = await self.role_repo.create(role_data)
        
        # Assign permissions if provided
        if role_data.permissions:
            await self.assign_permissions(str(role.id), role_data.permissions)
            
        return role
    
    async def get_role(self, role_id: str) -> Optional[Dict[str, Any]]:
        """Get a role by ID"""
        role = await self.role_repo.get(role_id)
        if not role:
            return None
            
        # Get permissions
        permissions = await self.role_repo.get_role_permissions(role_id)
        
        # Convert to dict and add permissions
        role_dict = dict(role.__dict__)
        role_dict["permission_names"] = list(permissions)
        
        return role_dict
    
    async def get_all_roles(self, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """Get all roles with pagination"""
        roles = await self.role_repo.get_all(skip, limit)
        
        # Add permissions to each role
        result = []
        for role in roles:
            permissions = await self.role_repo.get_role_permissions(str(role.id))
            role_dict = dict(role.__dict__)
            role_dict["permission_names"] = list(permissions)
            result.append(role_dict)
            
        return result
    
    async def count_roles(self) -> int:
        """Count total number of roles"""
        return await self.role_repo.count()
    
    async def update_role(self, role_id: str, role_data: RoleUpdate) -> Dict[str, Any]:
        """Update a role"""
        # Check if role exists
        role = await self.role_repo.get(role_id)
        if not role:
            raise ValueError(f"Role with ID '{role_id}' not found")
            
        # Check if new name is already taken
        if role_data.name and role_data.name != role.name:
            existing_role = await self.role_repo.get_by_name(role_data.name)
            if existing_role and str(existing_role.id) != role_id:
                raise ValueError(f"Role with name '{role_data.name}' already exists")
                
        # Update role
        updated_role = await self.role_repo.update(role_id, role_data.dict(exclude_unset=True))
        
        # Get permissions
        permissions = await self.role_repo.get_role_permissions(role_id)
        
        # Convert to dict and add permissions
        updated_dict = dict(updated_role.__dict__)
        updated_dict["permission_names"] = list(permissions)
        
        return updated_dict
    
    async def delete_role(self, role_id: str) -> bool:
        """Delete a role"""
        return await self.role_repo.delete(role_id)
    
    async def assign_permissions(self, role_id: str, permissions: List[str]) -> bool:
        """Assign permissions to a role"""
        # Check if role exists
        role = await self.role_repo.get(role_id)
        if not role:
            raise ValueError(f"Role with ID '{role_id}' not found")
            
        # Assign permissions
        return await self.role_repo.set_permissions(role_id, permissions)
    
    async def assign_role_to_user(self, role_id: str, user_id: str) -> bool:
        """Assign a role to a user"""
        # Check if role exists
        role = await self.role_repo.get(role_id)
        if not role:
            raise ValueError(f"Role with ID '{role_id}' not found")
            
        # Check if user exists
        user = await self.user_repo.get(user_id)
        if not user:
            raise ValueError(f"User with ID '{user_id}' not found")
            
        # Assign role to user
        return await self.role_repo.assign_to_user(role_id, user_id)
    
    async def remove_role_from_user(self, role_id: str, user_id: str) -> bool:
        """Remove a role from a user"""
        # Check if role exists
        role = await self.role_repo.get(role_id)
        if not role:
            raise ValueError(f"Role with ID '{role_id}' not found")
            
        # Check if user exists
        user = await self.user_repo.get(user_id)
        if not user:
            raise ValueError(f"User with ID '{user_id}' not found")
            
        # Remove role from user
        return await self.role_repo.remove_from_user(role_id, user_id)
