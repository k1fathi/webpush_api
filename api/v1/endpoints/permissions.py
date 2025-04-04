import logging
from typing import Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from fastapi.responses import JSONResponse

from api.deps import get_current_active_user
from core.exceptions.http import NotFoundException
from core.permissions.dependencies import has_permission
from models.domain.user import UserModel
from models.domain.permission import PermissionModel
from models.schemas.permission import (
    PermissionCreate, PermissionRead, PermissionUpdate, PermissionList
)
from services.permission import PermissionService
from utils.audit import audit_log

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get(
    "/",
    response_model=PermissionList,
    dependencies=[Depends(has_permission("list_permissions"))]
)
async def list_permissions(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    category: Optional[str] = None,
    permission_service: PermissionService = Depends(),
):
    """List all permissions with pagination"""
    try:
        permissions = await permission_service.get_all_permissions(skip, limit, category)
        total = len(permissions)  # In a real app, you'd use a separate count query
        
        return {
            "items": permissions,
            "total": total,
            "skip": skip,
            "limit": limit
        }
    except Exception as e:
        logger.error(f"Error listing permissions: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error listing permissions: {str(e)}"
        )

@router.get(
    "/{permission_name}",
    response_model=PermissionRead,
    dependencies=[Depends(has_permission("read_permission"))]
)
async def get_permission(
    permission_name: str = Path(...),
    permission_service: PermissionService = Depends(),
):
    """Get a permission by name"""
    permission = await permission_service.get_permission(permission_name)
    if not permission:
        raise NotFoundException("Permission not found")
    return permission

@router.get(
    "/for-user/{user_id}",
    response_model=List[str],
    dependencies=[Depends(has_permission("read_permission"))]
)
async def get_user_permissions(
    user_id: str = Path(...),
    permission_service: PermissionService = Depends(),
):
    """Get all permissions for a user"""
    try:
        permissions = await permission_service.get_user_permissions(user_id)
        return list(permissions)
    except Exception as e:
        logger.error(f"Error getting user permissions: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting user permissions: {str(e)}"
        )

@router.get(
    "/for-role/{role_name}",
    response_model=List[str],
    dependencies=[Depends(has_permission("read_permission"))]
)
async def get_role_permissions(
    role_name: str = Path(...),
    permission_service: PermissionService = Depends(),
):
    """Get all permissions for a role"""
    try:
        # For this endpoint, we'd need a method in the permission service to get 
        # permissions by role name rather than ID
        role_permissions = await permission_service.get_permissions_by_role_name(role_name)
        return role_permissions
    except Exception as e:
        logger.error(f"Error getting role permissions: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting role permissions: {str(e)}"
        )

@router.post(
    "/check",
    dependencies=[Depends(has_permission("read_permission"))]
)
async def check_permission(
    permission_name: str,
    user_id: Optional[str] = None,
    current_user: UserModel = Depends(get_current_active_user),
    permission_service: PermissionService = Depends(),
):
    """Check if a user has a specific permission"""
    try:
        # If user_id is not provided, use the current user
        check_user_id = user_id if user_id else str(current_user.id)
        
        has_perm = await permission_service.user_has_permission(
            check_user_id, permission_name
        )
        
        return {"user_id": check_user_id, "permission": permission_name, "has_permission": has_perm}
    except Exception as e:
        logger.error(f"Error checking permission: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error checking permission: {str(e)}"
        )
