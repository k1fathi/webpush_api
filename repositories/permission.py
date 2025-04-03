from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.orm import Session

from models.domain.permission import PermissionModel
from repositories.base import BaseRepository

class PermissionRepository(BaseRepository):
    """Repository for permission operations"""
    
    def __init__(self, session: Session):
        """Initialize with session"""
        self.session = session
    
    async def get_by_name(self, name: str) -> Optional[PermissionModel]:
        """Get a permission by name"""
        query = select(PermissionModel).where(PermissionModel.name == name)
        result = await self.session.execute(query)
        return result.scalars().first()
    
    async def get_all(self) -> List[PermissionModel]:
        """Get all permissions"""
        query = select(PermissionModel)
        result = await self.session.execute(query)
        return list(result.scalars().all())
