import logging
from typing import Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from fastapi.responses import JSONResponse

from api.deps import get_current_active_user
from core.exceptions.http import NotFoundException
from core.permissions.dependencies import has_permission
from models.domain.user import UserModel
from models.schemas.role import RoleCreate, RoleRead, RoleUpdate, RoleList
from services.role import RoleService
from utils.audit import audit_log

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get(
    "/",
    response_model=RoleList,
    dependencies=[Depends(has_permission("list_roles"))]
)
async def list_roles(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    role_service: RoleService = Depends(),
):
    """List all roles with pagination"""
    try:
        roles = await role_service.get_all_roles(skip, limit)
        total = await role_service.count_roles()
        
        return {
            "items": roles,
            "total": total,
            "skip": skip,
            "limit": limit
        }
    except Exception as e:
        logger.error(f"Error listing roles: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error listing roles: {str(e)}"
        )

@router.get(
    "/{role_id}",
    response_model=RoleRead,
    dependencies=[Depends(has_permission("read_role"))]
)
async def get_role(
    role_id: str = Path(...),
    role_service: RoleService = Depends(),
):
    """Get a role by ID"""
    role = await role_service.get_role(role_id)
    if not role:
        raise NotFoundException("Role not found")
    return role

@router.post(
    "/",
    response_model=RoleRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(has_permission("create_role"))]
)
async def create_role(
    role: RoleCreate,
    current_user: UserModel = Depends(get_current_active_user),
    role_service: RoleService = Depends(),
):
    """Create a new role"""
    try:
        created_role = await role_service.create_role(role)
        
        audit_log(
            f"Role '{role.name}' created",
            user_id=str(current_user.id),
            action_type="create_role",
            resource_type="role"
        )
        
        return created_role
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error creating role: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating role: {str(e)}"
        )

@router.put(
    "/{role_id}",
    response_model=RoleRead,
    dependencies=[Depends(has_permission("update_role"))]
)
async def update_role(
    role_id: str,
    role: RoleUpdate,
    current_user: UserModel = Depends(get_current_active_user),
    role_service: RoleService = Depends(),
):
    """Update a role"""
    try:
        updated_role = await role_service.update_role(role_id, role)
        
        audit_log(
            f"Role '{updated_role.name}' updated",
            user_id=str(current_user.id),
            action_type="update_role",
            resource_type="role",
            resource_id=role_id
        )
        
        return updated_role
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error updating role: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating role: {str(e)}"
        )

@router.delete(
    "/{role_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(has_permission("delete_role"))]
)
async def delete_role(
    role_id: str = Path(...),
    current_user: UserModel = Depends(get_current_active_user),
    role_service: RoleService = Depends(),
):
    """Delete a role"""
    try:
        role = await role_service.get_role(role_id)
        if not role:
            raise NotFoundException("Role not found")
            
        result = await role_service.delete_role(role_id)
        
        audit_log(
            f"Role '{role.name}' deleted",
            user_id=str(current_user.id),
            action_type="delete_role",
            resource_type="role",
            resource_id=role_id
        )
        
    except NotFoundException:
        raise
    except Exception as e:
        logger.error(f"Error deleting role: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting role: {str(e)}"
        )

@router.post(
    "/{role_id}/permissions",
    dependencies=[Depends(has_permission("update_role"))]
)
async def assign_permissions_to_role(
    role_id: str,
    permissions: List[str],
    current_user: UserModel = Depends(get_current_active_user),
    role_service: RoleService = Depends(),
):
    """Assign permissions to a role"""
    try:
        # Check if role exists
        role = await role_service.get_role(role_id)
        if not role:
            raise NotFoundException("Role not found")
            
        result = await role_service.assign_permissions(role_id, permissions)
        
        audit_log(
            f"Permissions assigned to role '{role.name}'",
            user_id=str(current_user.id),
            action_type="assign_permissions",
            resource_type="role",
            resource_id=role_id,
            metadata={"permissions": permissions}
        )
        
        return {"success": True, "assigned_permissions": permissions}
    except NotFoundException:
        raise
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error assigning permissions: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error assigning permissions: {str(e)}"
        )

@router.post(
    "/{role_id}/users/{user_id}",
    dependencies=[Depends(has_permission("update_role"))]
)
async def assign_role_to_user(
    role_id: str,
    user_id: str,
    current_user: UserModel = Depends(get_current_active_user),
    role_service: RoleService = Depends(),
):
    """Assign a role to a user"""
    try:
        # Check if role exists
        role = await role_service.get_role(role_id)
        if not role:
            raise NotFoundException("Role not found")
            
        result = await role_service.assign_role_to_user(role_id, user_id)
        
        audit_log(
            f"Role '{role.name}' assigned to user {user_id}",
            user_id=str(current_user.id),
            action_type="assign_role",
            resource_type="user",
            resource_id=user_id,
            metadata={"role_id": role_id}
        )
        
        return {"success": True, "role_id": role_id, "user_id": user_id}
    except NotFoundException:
        raise
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error assigning role to user: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error assigning role to user: {str(e)}"
        )

@router.delete(
    "/{role_id}/users/{user_id}",
    dependencies=[Depends(has_permission("update_role"))]
)
async def remove_role_from_user(
    role_id: str,
    user_id: str,
    current_user: UserModel = Depends(get_current_active_user),
    role_service: RoleService = Depends(),
):
    """Remove a role from a user"""
    try:
        # Check if role exists
        role = await role_service.get_role(role_id)
        if not role:
            raise NotFoundException("Role not found")
            
        result = await role_service.remove_role_from_user(role_id, user_id)
        
        audit_log(
            f"Role '{role.name}' removed from user {user_id}",
            user_id=str(current_user.id),
            action_type="remove_role",
            resource_type="user",
            resource_id=user_id,
            metadata={"role_id": role_id}
        )
        
        return {"success": True, "role_id": role_id, "user_id": user_id}
    except NotFoundException:
        raise
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error removing role from user: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error removing role from user: {str(e)}"
        )
