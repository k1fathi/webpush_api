import logging
from datetime import datetime
from typing import Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from pydantic import BaseModel, validator

from api.deps import get_current_active_user
from core.exceptions.http import NotFoundException
from core.permissions.dependencies import has_permission
from models.domain.user import UserModel
from models.schemas.notification import NotificationCreate, NotificationRead
from models.schemas.webpush import PushSubscriptionCreate
from services.user import UserService
from services.webpush import WebPushService
from utils.audit import audit_log

router = APIRouter()
logger = logging.getLogger(__name__)

class VapidPublicKey(BaseModel):
    publicKey: str

@router.get("/vapid-public-key", response_model=VapidPublicKey)
async def get_vapid_public_key():
    """Get the VAPID public key for WebPush subscription"""
    webpush_service = WebPushService()
    return {"publicKey": webpush_service.get_vapid_public_key()}

@router.post("/subscribe", status_code=status.HTTP_201_CREATED)
async def subscribe(
    subscription: PushSubscriptionCreate,
    user_service: UserService = Depends(),
    webpush_service: WebPushService = Depends(),
):
    """
    Subscribe a user to WebPush notifications.
    This endpoint is typically called from the frontend after getting permission.
    """
    try:
        # Check if existing user with the provided info
        existing_user = await user_service.get_by_email(subscription.email)
        
        if existing_user:
            # Update existing user
            existing_user.push_token = subscription.subscription_json
            existing_user.browser = subscription.browser
            existing_user.device_info = subscription.device_info
            existing_user.opted_in = True
            existing_user.last_activity = datetime.utcnow()
            
            updated_user = await user_service.update(existing_user.id, existing_user)
            audit_log(f"User {existing_user.id} updated WebPush subscription")
            return {"success": True, "userId": str(updated_user.id)}
            
        else:
            # Create new user
            new_user = await user_service.create({
                "email": subscription.email,
                "name": subscription.name if subscription.name else subscription.email,
                "push_token": subscription.subscription_json,
                "browser": subscription.browser,
                "device_info": subscription.device_info,
                "opted_in": True,
                "subscription_date": datetime.utcnow(),
                "last_activity": datetime.utcnow(),
                "custom_attributes": subscription.custom_attributes or {}
            })
            
            audit_log(f"New user {new_user.id} subscribed to WebPush")
            return {"success": True, "userId": str(new_user.id)}
            
    except Exception as e:
        logger.error(f"Error subscribing to WebPush: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error subscribing to WebPush: {str(e)}"
        )

@router.post("/unsubscribe")
async def unsubscribe(
    email: str,
    user_service: UserService = Depends(),
):
    """Unsubscribe a user from WebPush notifications"""
    try:
        user = await user_service.get_by_email(email)
        
        if not user:
            raise NotFoundException("User not found")
        
        user.opted_in = False
        user.last_activity = datetime.utcnow()
        await user_service.update(user.id, user)
        
        audit_log(f"User {user.id} unsubscribed from WebPush")
        return {"success": True}
        
    except Exception as e:
        logger.error(f"Error unsubscribing from WebPush: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error unsubscribing from WebPush: {str(e)}"
        )

@router.get("/track/{notification_id}/open")
async def track_open(
    notification_id: str = Path(...),
    webpush_service: WebPushService = Depends(),
):
    """Track when a notification is opened - called from the service worker"""
    success = webpush_service.track_open(notification_id)
    if not success:
        raise NotFoundException("Notification not found")
    
    return {"success": True}

@router.get("/track/{notification_id}/click")
async def track_click(
    notification_id: str = Path(...),
    redirect_url: Optional[str] = Query(None),
    webpush_service: WebPushService = Depends(),
):
    """Track when a notification is clicked - called from the service worker"""
    success = webpush_service.track_click(notification_id)
    if not success:
        raise NotFoundException("Notification not found")
    
    # If a redirect URL is provided, return it for the frontend to handle
    if redirect_url:
        return {"success": True, "redirectUrl": redirect_url}
    
    return {"success": True}

@router.post(
    "/send-test",
    response_model=NotificationRead,
    dependencies=[Depends(has_permission("create_notification"))]
)
async def send_test_notification(
    notification: NotificationCreate,
    current_user: UserModel = Depends(get_current_active_user),
    webpush_service: WebPushService = Depends(),
):
    """Send a test notification to the current user"""
    # Implementation would create and send a notification to the current user
    # This is a simplified placeholder that would be expanded in a real implementation
    return {"id": "test-notification-id", **notification.dict(), "sent_at": datetime.utcnow()}
