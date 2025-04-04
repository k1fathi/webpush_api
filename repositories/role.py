from typing import List, Optional, Set
from sqlalchemy import select
from sqlalchemy.orm import Session

from models.domain.role import RoleModel
from models.domain.role_permission import RolePermissionModel
from repositories.base import BaseRepository

class RoleRepository(BaseRepository):
    """Repository for role operations"""
    
    def __init__(self, session: Session):
        """Initialize with session"""
        self.session = session
    
    async def get_role_permissions(self, role_id: str) -> Set[str]:
        """Get all permissions for a role"""
        query = select(RolePermissionModel.permission_name).where(
            RolePermissionModel.role_id == role_id
        )
        result = await self.session.execute(query)
        return {row[0] for row in result}
        
    async def get_by_name(self, name: str) -> Optional[RoleModel]:
        """Get a role by name"""
        query = select(RoleModel).where(RoleModel.name == name)
        result = await self.session.execute(query)
        return result.scalars().first()
