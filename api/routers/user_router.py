from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from datetime import datetime
from core.dependencies import get_current_user, get_user_service
from core.permissions import require_permissions, Permission
from schemas.user_schema import (
    UserCreate, UserUpdate, UserResponse, 
    UserSegmentResponse, UserDeviceCreate,
    UserPreferencesUpdate, UserActivityResponse
)

# Remove prefix as it's handled in __init__.py
router = APIRouter()

# User Management Endpoints
@router.post("/", response_model=UserResponse)
@require_permissions([Permission.USER_MANAGEMENT])
async def create_user(
    user_in: UserCreate,
    user_service = Depends(get_user_service)
):
    """Create new user (Admin only)"""
    return await user_service.create_user(user_in.dict())

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user = Depends(get_current_user)
):
    """Get current user information"""
    return current_user

@router.get("/{user_id}", response_model=UserResponse)
@require_permissions([Permission.USER_MANAGEMENT])
async def get_user(
    user_id: int,
    user_service = Depends(get_user_service)
):
    """Get user by ID"""
    return await user_service.get_user(user_id)

@router.put("/{user_id}", response_model=UserResponse)
@require_permissions([Permission.USER_MANAGEMENT])
async def update_user(
    user_id: int,
    user_in: UserUpdate,
    user_service = Depends(get_user_service)
):
    """Update user information"""
    return await user_service.update_user(user_id, user_in)

# User Segment Management
@router.get("/{user_id}/segments", response_model=List[UserSegmentResponse])
@require_permissions([Permission.USER_MANAGEMENT])
async def get_user_segments(
    user_id: int,
    user_service = Depends(get_user_service)
):
    """Get user segments"""
    return await user_service.get_user_segments(user_id)

@router.post("/{user_id}/segments/{segment_id}")
@require_permissions([Permission.USER_MANAGEMENT])
async def add_user_to_segment(
    user_id: int,
    segment_id: int,
    user_service = Depends(get_user_service)
):
    """Add user to segment"""
    return await user_service.add_to_segment(user_id, segment_id)

# User Device Management
@router.post("/{user_id}/devices", response_model=UserResponse)
async def register_device(
    user_id: int,
    device: UserDeviceCreate,
    user_service = Depends(get_user_service),
    current_user = Depends(get_current_user)
):
    """Register user device for notifications"""
    if current_user.user_id != user_id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized")
    return await user_service.register_device(user_id, device)

# User Preferences
@router.put("/{user_id}/preferences", response_model=UserResponse)
async def update_preferences(
    user_id: int,
    preferences: UserPreferencesUpdate,
    user_service = Depends(get_user_service),
    current_user = Depends(get_current_user)
):
    """Update user notification preferences"""
    if current_user.user_id != user_id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized")
    return await user_service.update_preferences(user_id, preferences)

# User Activity
@router.get("/{user_id}/activity", response_model=List[UserActivityResponse])
@require_permissions([Permission.USER_MANAGEMENT])
async def get_user_activity(
    user_id: int,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    limit: int = Query(50, le=100),
    user_service = Depends(get_user_service)
):
    """Get user activity history"""
    return await user_service.get_activity(user_id, start_date, end_date, limit)

# Bulk Operations
@router.post("/bulk/create", response_model=List[UserResponse])
@require_permissions([Permission.USER_MANAGEMENT])
async def bulk_create_users(
    users: List[UserCreate],
    user_service = Depends(get_user_service)
):
    """Bulk create users"""
    return await user_service.bulk_create(users)

@router.post("/bulk/segment/{segment_id}")
@require_permissions([Permission.USER_MANAGEMENT])
async def bulk_add_to_segment(
    segment_id: int,
    user_ids: List[int],
    user_service = Depends(get_user_service)
):
    """Bulk add users to segment"""
    return await user_service.bulk_add_to_segment(segment_id, user_ids)

# Search and Filter
@router.get("/search/", response_model=List[UserResponse])
@require_permissions([Permission.USER_MANAGEMENT])
async def search_users(
    query: str,
    segment: Optional[str] = None,
    active_only: bool = True,
    limit: int = Query(50, le=100),
    user_service = Depends(get_user_service)
):
    """Search users with filters"""
    return await user_service.search(query, segment, active_only, limit)

# Analytics
@router.get("/{user_id}/analytics")
@require_permissions([Permission.ANALYTICS_ACCESS])
async def get_user_analytics(
    user_id: int,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    user_service = Depends(get_user_service)
):
    """Get user engagement analytics"""
    return await user_service.get_analytics(user_id, start_date, end_date)
