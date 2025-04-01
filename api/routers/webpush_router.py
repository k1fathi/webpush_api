from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from services.webpush_service import WebPushService
from core.dependencies import get_current_user, get_webpush_service
from core.permissions import require_permissions, Permission
from schemas.webpush_schema import WebPushCreate, WebPushUpdate, WebPushResponse

router = APIRouter()

@router.post("/", response_model=WebPushResponse)
@require_permissions([Permission.CAMPAIGN_MANAGEMENT])
async def create_webpush(
    webpush_in: WebPushCreate,
    webpush_service: WebPushService = Depends(get_webpush_service),
    current_user = Depends(get_current_user)
):
    """Create new WebPush notification"""
    return await webpush_service.create_notification(webpush_in)

@router.get("/{webpush_id}", response_model=WebPushResponse)
async def get_webpush(
    webpush_id: int,
    webpush_service: WebPushService = Depends(get_webpush_service)
):
    """Get WebPush notification by ID"""
    notification = await webpush_service.get_notification(webpush_id)
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    return notification

@router.put("/{webpush_id}/status", response_model=WebPushResponse)
async def update_webpush_status(
    webpush_id: int,
    status: str,
    webpush_service: WebPushService = Depends(get_webpush_service)
):
    """Update WebPush notification status"""
    notification = await webpush_service.update_status(webpush_id, status)
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    return notification

@router.get("/campaign/{campaign_id}", response_model=List[WebPushResponse])
@require_permissions([Permission.CAMPAIGN_MANAGEMENT])
async def get_campaign_notifications(
    campaign_id: int,
    webpush_service: WebPushService = Depends(get_webpush_service)
):
    """Get all notifications for a campaign"""
    return await webpush_service.get_campaign_notifications(campaign_id)
