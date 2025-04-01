from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from typing import List, Optional

from core.config import settings
from core.exceptions.http import ForbiddenException, UnauthorizedException
from models.domain.user import User
from models.domain.role import RoleModel
from services.user import UserService
from .permission import PERMISSIONS

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_PREFIX}/auth/login")

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    user_service: UserService = Depends(),
) -> User:
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            raise UnauthorizedException()
    except JWTError:
        raise UnauthorizedException()
    
    user = await user_service.get(user_id)
    if user is None:
        raise UnauthorizedException()
    
    return user

async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

def has_permission(permission_name: str):
    async def permission_checker(
        current_user: User = Depends(get_current_active_user),
    ):
        # System administrator role has all permissions
        if any(role.name == "system_administrator" for role in current_user.roles):
            return True
        
        # Check if user has the required permission in any of their roles
        user_permissions = set()
        for role in current_user.roles:
            for perm in role.permissions:
                user_permissions.add(perm)
        
        if permission_name not in user_permissions:
            raise ForbiddenException(
                f"User does not have permission to {permission_name}"
            )
        
        return True
    
    return permission_checker

def has_any_permission(permission_names: List[str]):
    async def permission_checker(
        current_user: User = Depends(get_current_active_user),
    ):
        # System administrator role has all permissions
        if any(role.name == "system_administrator" for role in current_user.roles):
            return True
        
        # Check if user has any of the required permissions in their roles
        user_permissions = set()
        for role in current_user.roles:
            for perm in role.permissions:
                user_permissions.add(perm)
        
        if not any(perm in user_permissions for perm in permission_names):
            raise ForbiddenException(
                f"User does not have any of the required permissions: {', '.join(permission_names)}"
            )
        
        return True
    
    return permission_checker
