"""API routes for managing user webpush subscriptions"""
import uuid
import logging
from typing import Dict, List, Any, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Body, Path, status
from fastapi.responses import JSONResponse

from api import deps
from api.deps import get_current_active_user
from core.exceptions.http import NotFoundException
from core.permissions.dependencies import has_permission
from models.domain.user import UserModel
from models.schemas.subscription import (
    SubscriptionCreate, SubscriptionRead, SubscriptionUpdate, SubscriptionList
)
from models.schemas.user import UserRole
from services import subscription_service
from services.subscription import SubscriptionService
from services.user import UserService

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post(
    "/",
    response_model=SubscriptionRead,
    status_code=status.HTTP_201_CREATED
)
async def create_subscription(
    subscription: SubscriptionCreate,
    current_user: Optional[UserModel] = Depends(get_current_active_user),
    subscription_service: SubscriptionService = Depends(),
):
    """Create a new subscription"""
    try:
        # Automatically associate with current user if authenticated
        if current_user and not subscription.user_id:
            subscription.user_id = str(current_user.id)
        
        created_subscription = await subscription_service.create_subscription(subscription)
        return created_subscription
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error creating subscription: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating subscription: {str(e)}"
        )

@router.get(
    "/",
    response_model=SubscriptionList,
    dependencies=[Depends(has_permission("list_subscriptions"))]
)
async def list_subscriptions(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    user_id: Optional[str] = None,
    is_active: Optional[bool] = None,
    subscription_service: SubscriptionService = Depends(),
):
    """List all subscriptions with pagination"""
    try:
        subscriptions, total = await subscription_service.get_all_subscriptions(
            skip, limit, user_id, is_active
        )
        return {
            "items": subscriptions,
            "total": total,
            "page": skip // limit + 1,
            "page_size": limit
        }
    except Exception as e:
        logger.error(f"Error listing subscriptions: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error listing subscriptions: {str(e)}"
        )

@router.get(
    "/{subscription_id}",
    response_model=SubscriptionRead,
    dependencies=[Depends(has_permission("read_subscription"))]
)
async def get_subscription(
    subscription_id: str = Path(...),
    subscription_service: SubscriptionService = Depends(),
):
    """Get a subscription by ID"""
    subscription = await subscription_service.get_subscription(subscription_id)
    if not subscription:
        raise NotFoundException("Subscription not found")
    return subscription

@router.put(
    "/{subscription_id}",
    response_model=SubscriptionRead,
    dependencies=[Depends(has_permission("update_subscription"))]
)
async def update_subscription(
    subscription_id: str,
    subscription: SubscriptionUpdate,
    subscription_service: SubscriptionService = Depends(),
):
    """Update a subscription"""
    try:
        updated_subscription = await subscription_service.update_subscription(
            subscription_id, subscription
        )
        if not updated_subscription:
            raise NotFoundException("Subscription not found")
        return updated_subscription
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error updating subscription: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating subscription: {str(e)}"
        )

@router.delete(
    "/{subscription_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(has_permission("delete_subscription"))]
)
async def delete_subscription(
    subscription_id: str = Path(...),
    subscription_service: SubscriptionService = Depends(),
):
    """Delete a subscription"""
    result = await subscription_service.delete_subscription(subscription_id)
    if not result:
        raise NotFoundException("Subscription not found")

@router.get(
    "/user/{user_id}",
    response_model=list[SubscriptionRead],
    dependencies=[Depends(has_permission("read_subscription"))]
)
async def get_user_subscriptions(
    user_id: str = Path(...),
    user_service: UserService = Depends(),
    subscription_service: SubscriptionService = Depends(),
):
    """Get all active subscriptions for a user"""
    # Check if user exists
    user = await user_service.get_user(user_id)
    if not user:
        raise NotFoundException("User not found")
        
    subscriptions = await subscription_service.get_active_subscriptions_by_user(user_id)
    return subscriptions
