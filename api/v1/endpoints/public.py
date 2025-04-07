"""Public API endpoints that don't require authentication"""
import uuid
from datetime import datetime
from typing import Dict, Any

from fastapi import APIRouter, Depends, HTTPException, Body, status
from sqlalchemy.ext.asyncio import AsyncSession

from api import deps
from services import subscription_service
from models.schemas.subscription import SubscriptionCreate, SubscriptionUpdate

router = APIRouter()

@router.post(
    "/subscribe", 
    response_model=Dict[str, str],
    summary="Subscribe to notifications",
    description="Public endpoint for users to subscribe to web push notifications"
)
async def subscribe(
    subscription_data: SubscriptionCreate = Body(...),
    user_id: uuid.UUID = Body(..., description="User ID"),
    db: AsyncSession = Depends(deps.get_db)
):
    """Subscribe to push notifications"""
    # Create subscription data dictionary
    sub_info = subscription_data.subscription_info.dict()
    
    # Add metadata
    metadata = {
        "user_agent": subscription_data.user_agent,
        "device_type": subscription_data.device_type,
        "subscribed_at": str(datetime.utcnow())
    }
    
    # Combine with existing subscription data
    success = await subscription_service.update_subscription(
        db, 
        user_id, 
        {
            "push_subscription": sub_info,
            "metadata": metadata
        }
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return {"status": "success", "message": "Subscription created successfully"}


@router.post(
    "/unsubscribe",
    response_model=Dict[str, str],
    summary="Unsubscribe from notifications",
    description="Public endpoint for users to unsubscribe from web push notifications"
)
async def unsubscribe(
    endpoint: str = Body(..., embed=True, description="Push subscription endpoint"),
    user_id: uuid.UUID = Body(..., embed=True, description="User ID"),
    db: AsyncSession = Depends(deps.get_db)
):
    """Unsubscribe from push notifications"""
    user_sub = await subscription_service.get_subscription_by_user_id(db, user_id)
    if not user_sub or "subscription_info" not in user_sub:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subscription not found"
        )
    
    # Get current subscription info
    sub_info = user_sub["subscription_info"]
    
    # If the endpoint matches, mark as unsubscribed
    if "push_subscription" in sub_info and sub_info["push_subscription"].get("endpoint") == endpoint:
        # Keep the subscription info but mark as inactive
        sub_info["active"] = False
        sub_info["unsubscribed_at"] = str(datetime.utcnow())
        
        success = await subscription_service.update_subscription(db, user_id, sub_info)
        if success:
            return {"status": "success", "message": "Unsubscribed successfully"}
    
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Invalid subscription endpoint"
    )
