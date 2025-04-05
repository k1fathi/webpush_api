from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, status
from typing import Dict, List, Any, Optional

from models.schemas.notification import NotificationRead, NotificationCreate, DeliveryStatus
from models.schemas.webpush import WebPushNotification
from services.notification_delivery import NotificationDeliveryService
from api.deps import get_current_user, get_notification_delivery_service

router = APIRouter()

@router.post("/queue", status_code=status.HTTP_202_ACCEPTED)
async def queue_notification_delivery(
    notification: NotificationCreate,
    background_tasks: BackgroundTasks,
    service: NotificationDeliveryService = Depends(get_notification_delivery_service),
    current_user = Depends(get_current_user)
):
    """
    Queue a notification for delivery
    
    The notification will be processed asynchronously in the background
    """
    notification_id = await service.queue_notification(notification)
    background_tasks.add_task(service.process_notification, notification_id)
    
    return {
        "notification_id": notification_id,
        "status": "queued",
        "message": "Notification queued for delivery"
    }

@router.post("/batch", status_code=status.HTTP_202_ACCEPTED)
async def queue_bulk_notifications(
    notifications: List[NotificationCreate],
    background_tasks: BackgroundTasks,
    service: NotificationDeliveryService = Depends(get_notification_delivery_service),
    current_user = Depends(get_current_user)
):
    """
    Queue multiple notifications for delivery in batch
    
    Notifications will be processed asynchronously in the background
    """
    notification_ids = await service.queue_notifications_batch(notifications)
    background_tasks.add_task(service.process_notifications_batch, notification_ids)
    
    return {
        "notification_count": len(notification_ids),
        "notification_ids": notification_ids,
        "status": "queued",
        "message": "Notifications queued for delivery"
    }

@router.get("/status/{notification_id}", response_model=Dict[str, Any])
async def get_delivery_status(
    notification_id: str,
    service: NotificationDeliveryService = Depends(get_notification_delivery_service),
    current_user = Depends(get_current_user)
):
    """
    Get the delivery status of a specific notification
    """
    status_info = await service.get_notification_status(notification_id)
    if not status_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )
    return status_info

@router.post("/{notification_id}/retry", response_model=Dict[str, Any])
async def retry_notification_delivery(
    notification_id: str,
    background_tasks: BackgroundTasks,
    service: NotificationDeliveryService = Depends(get_notification_delivery_service),
    current_user = Depends(get_current_user)
):
    """
    Retry delivery for a failed notification
    """
    success = await service.reset_notification_for_retry(notification_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found or cannot be retried"
        )
    
    background_tasks.add_task(service.process_notification, notification_id)
    
    return {
        "notification_id": notification_id,
        "status": "queued",
        "message": "Notification requeued for delivery"
    }

@router.post("/test", status_code=status.HTTP_202_ACCEPTED)
async def send_test_notification(
    notification: WebPushNotification,
    user_id: str,
    background_tasks: BackgroundTasks,
    service: NotificationDeliveryService = Depends(get_notification_delivery_service),
    current_user = Depends(get_current_user)
):
    """
    Send a test notification to a specific user
    """
    notification_id = await service.create_test_notification(notification, user_id)
    background_tasks.add_task(service.process_notification, notification_id)
    
    return {
        "notification_id": notification_id,
        "status": "queued",
        "message": "Test notification queued for delivery"
    }

@router.get("/stats", response_model=Dict[str, Any])
async def get_delivery_stats(
    campaign_id: Optional[str] = None,
    service: NotificationDeliveryService = Depends(get_notification_delivery_service),
    current_user = Depends(get_current_user)
):
    """
    Get notification delivery statistics
    
    Optionally filtered by campaign_id
    """
    return await service.get_delivery_stats(campaign_id)

@router.get("/failed", response_model=List[NotificationRead])
async def list_failed_notifications(
    skip: int = 0,
    limit: int = 50,
    campaign_id: Optional[str] = None,
    service: NotificationDeliveryService = Depends(get_notification_delivery_service),
    current_user = Depends(get_current_user)
):
    """
    List notifications that failed to deliver
    """
    return await service.list_notifications_by_status(
        DeliveryStatus.FAILED, 
        skip=skip, 
        limit=limit,
        campaign_id=campaign_id
    )
