import logging
from typing import Dict, List, Optional, Any

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm

from api.deps import get_current_active_user
from core.exceptions.http import NotFoundException
from core.permissions.dependencies import has_permission
from models.domain.user import UserModel
from models.user import UserStatus
from models.schemas.user import (
    UserBase, UserCreate, UserRead, UserUpdate, UserList, 
    UserDevice, UserPreferences, UserStats
)
from services.user import UserService

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post(
    "/",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(has_permission("create_user"))]
)
async def create_user(
    user: UserCreate,
    user_service: UserService = Depends(),
):
    """Create a new user"""
    try:
        created_user = await user_service.create_user(user)
        return created_user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error creating user: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating user: {str(e)}"
        )

@router.get(
    "/",
    response_model=UserList,
    dependencies=[Depends(has_permission("list_users"))]
)
async def list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    status: Optional[UserStatus] = None,
    user_service: UserService = Depends(),
):
    """List all users with pagination"""
    try:
        users, total = await user_service.get_all_users(skip, limit, status)
        return {
            "items": users,
            "total": total,
            "page": skip // limit + 1,
            "page_size": limit
        }
    except Exception as e:
        logger.error(f"Error listing users: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error listing users: {str(e)}"
        )

@router.get(
    "/{user_id}",
    response_model=UserRead,
    dependencies=[Depends(has_permission("read_user"))]
)
async def get_user(
    user_id: str = Path(...),
    user_service: UserService = Depends(),
):
    """Get a user by ID"""
    user = await user_service.get_user(user_id)
    if not user:
        raise NotFoundException("User not found")
    return user

@router.put(
    "/{user_id}",
    response_model=UserRead,
    dependencies=[Depends(has_permission("update_user"))]
)
async def update_user(
    user_id: str,
    user: UserUpdate,
    user_service: UserService = Depends(),
):
    """Update a user"""
    try:
        updated_user = await user_service.update_user(user_id, user)
        return updated_user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error updating user: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating user: {str(e)}"
        )

@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(has_permission("delete_user"))]
)
async def delete_user(
    user_id: str = Path(...),
    user_service: UserService = Depends(),
):
    """Delete a user"""
    result = await user_service.delete_user(user_id)
    if not result:
        raise NotFoundException("User not found")

@router.post(
    "/token",
    response_model=Dict[str, str]
)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    user_service: UserService = Depends(),
):
    """Get an access token"""
    user = await user_service.authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = user_service.create_access_token(user.id)
    
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

@router.get(
    "/me",
    response_model=UserRead
)
async def read_users_me(
    current_user: UserModel = Depends(get_current_active_user),
):
    """Get current authenticated user"""
    return current_user

@router.post(
    "/{user_id}/activate",
    response_model=UserRead,
    dependencies=[Depends(has_permission("activate_user"))]
)
async def activate_user(
    user_id: str = Path(...),
    user_service: UserService = Depends(),
):
    """Activate a user"""
    try:
        activated_user = await user_service.activate_user(user_id)
        return activated_user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error activating user: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error activating user: {str(e)}"
        )

@router.post(
    "/{user_id}/deactivate",
    response_model=UserRead,
    dependencies=[Depends(has_permission("deactivate_user"))]
)
async def deactivate_user(
    user_id: str = Path(...),
    user_service: UserService = Depends(),
):
    """Deactivate a user"""
    try:
        deactivated_user = await user_service.deactivate_user(user_id)
        return deactivated_user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error deactivating user: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deactivating user: {str(e)}"
        )

@router.post(
    "/{user_id}/devices",
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(has_permission("update_user"))]
)
async def add_user_device(
    user_id: str,
    device: UserDevice,
    user_service: UserService = Depends(),
):
    """Add a device to a user"""
    try:
        result = await user_service.add_user_device(user_id, device)
        if result:
            return {"message": "Device added successfully"}
        else:
            return {"message": "Failed to add device"}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error adding device: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error adding device: {str(e)}"
        )

@router.put(
    "/{user_id}/notification-settings",
    response_model=UserRead,
    dependencies=[Depends(has_permission("update_user"))]
)
async def update_notification_settings(
    user_id: str,
    settings: UserPreferences,
    user_service: UserService = Depends(),
):
    """Update notification settings for a user"""
    try:
        updated_user = await user_service.update_notification_settings(
            user_id, 
            settings.dict()
        )
        return updated_user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error updating notification settings: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating notification settings: {str(e)}"
        )

@router.get(
    "/{user_id}/stats",
    response_model=UserStats,
    dependencies=[Depends(has_permission("read_user"))]
)
async def get_user_stats(
    user_id: str = Path(...),
    user_service: UserService = Depends(),
):
    """Get statistics for a user"""
    # Check if user exists
    user = await user_service.get_user(user_id)
    if not user:
        raise NotFoundException("User not found")
        
    stats = await user_service.get_user_stats(user_id)
    return stats
