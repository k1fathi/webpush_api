import logging
from datetime import datetime
from typing import Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from fastapi.responses import JSONResponse, RedirectResponse

from api.deps import get_current_active_user
from core.exceptions.http import NotFoundException
from core.permissions.dependencies import has_permission
from models.domain.user import UserModel
from models.schemas.notification import DeliveryStatus, NotificationRead, NotificationCreate, NotificationUpdate, NotificationList
from services.notification import NotificationService
from utils.audit import audit_log

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post(
    "/",
    response_model=NotificationRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(has_permission("create_notification"))]
)
async def create_notification(
    notification: NotificationCreate,
    current_user: UserModel = Depends(get_current_active_user),
    notification_service: NotificationService = Depends(),
):
    """Create a new notification"""
    try:
        created = await notification_service.create_notification(notification.dict())
        return created
    except Exception as e:
        logger.error(f"Error creating notification: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating notification: {str(e)}"
        )

@router.post(
    "/campaign/{campaign_id}",
    response_model=Dict,
    dependencies=[Depends(has_permission("create_notification"))]
)
async def create_campaign_notifications(
    campaign_id: str,
    user_ids: List[str],
    current_user: UserModel = Depends(get_current_active_user),
    notification_service: NotificationService = Depends(),
):
    """Create notifications for all users in a campaign"""
    try:
        notifications = await notification_service.create_notifications_for_campaign(
            campaign_id, user_ids
        )
        return {
            "success": True,
            "campaign_id": campaign_id,
            "notifications_created": len(notifications),
            "user_count": len(user_ids)
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error creating campaign notifications: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating campaign notifications: {str(e)}"
        )

@router.post(
    "/{notification_id}/send",
    response_model=Dict,
    dependencies=[Depends(has_permission("send_notification"))]
)
async def send_notification(
    notification_id: str,
    current_user: UserModel = Depends(get_current_active_user),
    notification_service: NotificationService = Depends(),
):
    """Send a notification"""
    try:
        result = await notification_service.send_notification(notification_id)
        if result:
            return {
                "success": True,
                "notification_id": notification_id,
                "status": "sent"
            }
        else:
            return {
                "success": False,
                "notification_id": notification_id,
                "status": "failed"
            }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error sending notification: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error sending notification: {str(e)}"
        )

@router.get(
    "/{notification_id}",
    response_model=NotificationRead,
    dependencies=[Depends(has_permission("read_notification"))]
)
async def get_notification(
    notification_id: str,
    notification_service: NotificationService = Depends(),
):
    """Get a notification by ID"""
    notification = await notification_service.get_notification(notification_id)
    if not notification:
        raise NotFoundException("Notification not found")
    return notification

@router.get(
    "/user/{user_id}",
    response_model=NotificationList,
    dependencies=[Depends(has_permission("read_notification"))]
)
async def get_user_notifications(
    user_id: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    notification_service: NotificationService = Depends(),
):
    """Get notifications for a user"""
    skip = (page - 1) * page_size
    notifications = await notification_service.get_notifications_for_user(
        user_id, skip, page_size
    )
    
    # Count total for pagination info
    total = len(notifications)  # This would need to be a separate count query in a real application
    
    return {
        "items": notifications,
        "total": total,
        "page": page,
        "page_size": page_size
    }

@router.get(
    "/campaign/{campaign_id}/stats",
    dependencies=[Depends(has_permission("read_notification"))]
)
async def get_campaign_notification_stats(
    campaign_id: str,
    notification_service: NotificationService = Depends(),
):
    """Get notification statistics for a campaign"""
    try:
        stats = await notification_service.get_notification_stats(campaign_id)
        return stats
    except Exception as e:
        logger.error(f"Error getting notification stats: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting notification stats: {str(e)}"
        )

@router.get(
    "/track/{notification_id}/open",
    response_model=Dict
)
async def track_notification_open(
    notification_id: str,
    notification_service: NotificationService = Depends(),
):
    """Track when a notification is opened"""
    success = await notification_service.track_open(notification_id)
    if not success:
        raise NotFoundException("Notification not found")
    
    # Return a small transparent pixel
    return {"success": True}

@router.get(
    "/track/{notification_id}/click",
    response_class=RedirectResponse
)
async def track_notification_click(
    notification_id: str,
    redirect_url: Optional[str] = Query(None),
    notification_service: NotificationService = Depends(),
):
    """Track when a notification is clicked and redirect to target URL"""
    success = await notification_service.track_click(notification_id)
    if not success:
        raise NotFoundException("Notification not found")
    
    # Get the notification to find the redirect URL
    notification = await notification_service.get_notification(notification_id)
    
    # Redirect to the specified URL or notification's action URL
    target_url = redirect_url or notification.action_url or "/"
    return RedirectResponse(url=target_url)
