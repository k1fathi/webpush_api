"""API routes for managing user webpush subscriptions"""
import uuid
from typing import Dict, List, Any, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Body, Path, status
from sqlalchemy.ext.asyncio import AsyncSession

from api import deps
from services import subscription_service
from models.schemas.user import UserRole

router = APIRouter()

@router.get(
    "/", 
    response_model=List[Dict[str, Any]],
    summary="Get all subscriptions",
    description="Retrieve all user webpush subscriptions with pagination"
)
async def get_all_subscriptions(
    db: AsyncSession = Depends(deps.get_db),
    skip: int = Query(0, description="Number of records to skip"),
    limit: int = Query(100, description="Maximum number of records to return"),
    active_only: bool = Query(True, description="Only return active subscriptions"),
    current_user = Depends(deps.get_current_user_with_permissions(["subscriptions:read"]))
):
    """Get all subscriptions with pagination"""
    subscriptions = await subscription_service.get_all_subscriptions(
        db, 
        skip=skip, 
        limit=limit, 
        active_only=active_only
    )
    return subscriptions


@router.get(
    "/count",
    response_model=Dict[str, int],
    summary="Get subscription count",
    description="Get count of active subscriptions"
)
async def get_subscription_count(
    db: AsyncSession = Depends(deps.get_db),
    current_user = Depends(deps.get_current_user_with_permissions(["subscriptions:read"]))
):
    """Get count of active subscriptions"""
    count = await subscription_service.get_active_subscription_count(db)
    return {"count": count}


@router.get(
    "/user/{user_id}",
    response_model=Dict[str, Any],
    summary="Get user subscription",
    description="Get subscription details for a specific user"
)
async def get_user_subscription(
    user_id: uuid.UUID = Path(..., description="User ID"),
    db: AsyncSession = Depends(deps.get_db),
    current_user = Depends(deps.get_current_user_with_permissions(["subscriptions:read"]))
):
    """Get subscription for a specific user"""
    subscription = await subscription_service.get_subscription_by_user_id(db, user_id)
    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subscription not found"
        )
    return subscription


@router.get(
    "/segment/{segment_id}",
    response_model=List[Dict[str, Any]],
    summary="Get subscriptions by segment",
    description="Get subscriptions for users in a specific segment"
)
async def get_segment_subscriptions(
    segment_id: uuid.UUID = Path(..., description="Segment ID"),
    skip: int = Query(0, description="Number of records to skip"),
    limit: int = Query(100, description="Maximum number of records to return"),
    db: AsyncSession = Depends(deps.get_db),
    current_user = Depends(deps.get_current_user_with_permissions(["subscriptions:read", "segments:read"]))
):
    """Get subscriptions for users in a specific segment"""
    subscriptions = await subscription_service.get_subscriptions_by_segment_id(
        db,
        segment_id=segment_id,
        skip=skip,
        limit=limit
    )
    return subscriptions


@router.put(
    "/user/{user_id}",
    response_model=Dict[str, str],
    summary="Update user subscription",
    description="Update subscription information for a specific user"
)
async def update_user_subscription(
    user_id: uuid.UUID = Path(..., description="User ID"),
    subscription_data: Dict[str, Any] = Body(..., description="Subscription data"),
    db: AsyncSession = Depends(deps.get_db),
    current_user = Depends(deps.get_current_user_with_permissions(["subscriptions:write"]))
):
    """Update subscription for a specific user"""
    success = await subscription_service.update_subscription(db, user_id, subscription_data)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found or subscription update failed"
        )
    
    return {"status": "success", "message": "Subscription updated successfully"}
