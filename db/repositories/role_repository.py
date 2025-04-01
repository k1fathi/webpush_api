from .base_repository import BaseRepository
from db.models.roles_model import Role, Permission
from typing import List, Optional

class RoleRepository(BaseRepository[Role]):
    async def get_by_name(self, name: str) -> Optional[Role]:
        return self.db.query(Role).filter(Role.name == name).first()

    async def assign_permission(self, role_id: int, permission_id: int) -> bool:
        role = await self.get(role_id)
        if role:
            permission = self.db.query(Permission).get(permission_id)
            if permission and permission not in role.permissions:
                role.permissions.append(permission)
                self.db.commit()
                return True
        return False

    async def get_role_permissions(self, role_id: int) -> List[Permission]:
        role = await self.get(role_id)
        return role.permissions if role else []

class PermissionRepository(BaseRepository[Permission]):
    async def get_by_name(self, name: str) -> Optional[Permission]:
        return self.db.query(Permission).filter(Permission.name == name).first()
