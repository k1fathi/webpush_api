"""
Web Push API Endpoints
"""
from typing import Dict, List, Optional, Any
from fastapi import APIRouter, Depends, HTTPException, Body, Query, Path
from sqlalchemy.orm import Session

from core.dependencies import get_db
from services.web_push import WebPushService
from models.schemas.web_push_config import WebPushConfig, WebPushConfigCreate, WebPushConfigUpdate
from models.schemas.subscription import SubscriptionCreate, SubscriptionRead, SubscriptionUpdate, SubscriptionStats
from models.schemas.web_push_event import WebPushEventCreate, WebPushEvent, WebPushEventRead

router = APIRouter(prefix="/webpush", tags=["WebPush"])

# Subscription Endpoints
@router.post("/subscription", response_model=Dict[str, Any])
async def create_subscription(
    subscription_data: Dict[str, Any] = Body(...),
    db: Session = Depends(get_db)
):
    """
    Create or update a push subscription. Used by browsers to register for push notifications.
    """
    web_push_service = WebPushService(db)
    subscription = await web_push_service.create_subscription(subscription_data)
    
    return {
        "success": True,
        "subscription": subscription
    }

@router.delete("/subscription", response_model=Dict[str, bool])
async def delete_subscription(
    subscription_data: Dict[str, Any] = Body(...),
    db: Session = Depends(get_db)
):
    """
    Delete a push subscription. Used when a user unsubscribes.
    """
    from repositories.subscription import SubscriptionRepository
    repo = SubscriptionRepository(db)
    
    # Find subscription by endpoint
    subscription = repo.get_by_endpoint(subscription_data.get("endpoint", ""))
    
    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")
    
    # Delete the subscription
    success = repo.delete(subscription.id)
    
    return {"success": success}

@router.post("/subscription/preferences", response_model=Dict[str, bool])
async def update_subscription_preferences(
    data: Dict[str, Any] = Body(...),
    db: Session = Depends(get_db)
):
    """
    Update subscription preferences like frequency cap, quiet hours, etc.
    """
    from repositories.subscription import SubscriptionRepository
    repo = SubscriptionRepository(db)
    
    subscription_data = data.get("subscription", {})
    preferences = data.get("preferences", {})
    
    # Find subscription by endpoint
    subscription = repo.get_by_endpoint(subscription_data.get("endpoint", ""))
    
    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")
    
    # Update with new preferences
    update_data = SubscriptionUpdate(
        frequency_cap_daily=preferences.get("frequencyCapDaily"),
        quiet_hours_start=preferences.get("quietHoursStart"),
        quiet_hours_end=preferences.get("quietHoursEnd"),
        preferred_topics=preferences.get("preferredTopics"),
    )
    
    updated = repo.update(subscription.id, update_data)
    
    return {"success": updated is not None}

@router.post("/subscription/permission", response_model=Dict[str, bool])
async def update_subscription_permission(
    data: Dict[str, Any] = Body(...),
    db: Session = Depends(get_db)
):
    """
    Update subscription permission status.
    """
    from repositories.subscription import SubscriptionRepository
    repo = SubscriptionRepository(db)
    
    subscription_data = data.get("subscription", {})
    permission = data.get("permission")
    
    # Find subscription by endpoint
    subscription = repo.get_by_endpoint(subscription_data.get("endpoint", ""))
    
    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")
    
    # Update permission
    success = repo.update_permission_status(subscription.id, permission)
    
    return {"success": success}

@router.get("/subscription/stats", response_model=SubscriptionStats)
async def get_subscription_stats(
    db: Session = Depends(get_db)
):
    """
    Get subscription statistics.
    """
    from repositories.subscription import SubscriptionRepository
    repo = SubscriptionRepository(db)
    
    stats = repo.get_subscription_stats()
    
    return stats

# Events Endpoints
@router.post("/events", response_model=Dict[str, bool])
async def track_event(
    event_data: Dict[str, Any] = Body(...),
    db: Session = Depends(get_db)
):
    """
    Track a web push notification event (click, dismiss, etc.).
    """
    web_push_service = WebPushService(db)
    
    event_type = event_data.pop("eventType", "unknown")
    
    await web_push_service.track_event(event_type, event_data)
    
    return {"success": True}

@router.get("/events", response_model=List[WebPushEventRead])
async def get_events(
    notification_id: Optional[str] = Query(None),
    subscription_id: Optional[str] = Query(None),
    user_id: Optional[str] = Query(None),
    campaign_id: Optional[str] = Query(None),
    event_type: Optional[str] = Query(None),
    skip: int = Query(0),
    limit: int = Query(100),
    db: Session = Depends(get_db)
):
    """
    Get web push events with optional filtering.
    """
    from repositories.web_push_event import WebPushEventRepository
    repo = WebPushEventRepository(db)
    
    # Build filters
    filters = {}
    if notification_id:
        filters["notification_id"] = notification_id
    if subscription_id:
        filters["subscription_id"] = subscription_id
    if user_id:
        filters["user_id"] = user_id
    if campaign_id:
        filters["campaign_id"] = campaign_id
    if event_type:
        filters["event_type"] = event_type
    
    events = repo.list(skip=skip, limit=limit, filters=filters)
    
    return events

# Configuration Endpoints
@router.get("/config", response_model=WebPushConfig)
async def get_web_push_config(
    db: Session = Depends(get_db)
):
    """
    Get the default web push configuration.
    """
    web_push_service = WebPushService(db)
    
    config = await web_push_service.get_web_push_config()
    
    return config

@router.get("/config/{config_id}", response_model=WebPushConfig)
async def get_web_push_config_by_id(
    config_id: str = Path(...),
    db: Session = Depends(get_db)
):
    """
    Get a specific web push configuration by ID.
    """
    from repositories.web_push_config import WebPushConfigRepository
    repo = WebPushConfigRepository(db)
    
    config = repo.get(config_id)
    
    if not config:
        raise HTTPException(status_code=404, detail="Configuration not found")
    
    return config

@router.post("/config", response_model=WebPushConfig)
async def create_web_push_config(
    config: WebPushConfigCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new web push configuration.
    """
    from repositories.web_push_config import WebPushConfigRepository
    repo = WebPushConfigRepository(db)
    
    new_config = repo.create(config)
    
    return new_config

@router.put("/config/{config_id}", response_model=WebPushConfig)
async def update_web_push_config(
    config_id: str = Path(...),
    config: WebPushConfigUpdate = Body(...),
    db: Session = Depends(get_db)
):
    """
    Update an existing web push configuration.
    """
    from repositories.web_push_config import WebPushConfigRepository
    repo = WebPushConfigRepository(db)
    
    updated_config = repo.update(config_id, config)
    
    if not updated_config:
        raise HTTPException(status_code=404, detail="Configuration not found")
    
    return updated_config

@router.delete("/config/{config_id}", response_model=Dict[str, bool])
async def delete_web_push_config(
    config_id: str = Path(...),
    db: Session = Depends(get_db)
):
    """
    Delete a web push configuration.
    """
    from repositories.web_push_config import WebPushConfigRepository
    repo = WebPushConfigRepository(db)
    
    success = repo.delete(config_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Configuration not found or cannot be deleted")
    
    return {"success": success}

@router.post("/config/{config_id}/set-default", response_model=Dict[str, bool])
async def set_default_config(
    config_id: str = Path(...),
    db: Session = Depends(get_db)
):
    """
    Set a configuration as the default.
    """
    from repositories.web_push_config import WebPushConfigRepository
    repo = WebPushConfigRepository(db)
    
    success = repo.set_as_default(config_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Configuration not found")
    
    return {"success": success}

# Testing Endpoints
@router.post("/test", response_model=Dict[str, bool])
async def send_test_notification(
    data: Dict[str, Any] = Body(...),
    db: Session = Depends(get_db)
):
    """
    Send a test notification to a specific subscription.
    """
    from models.schemas.notification import Notification
    web_push_service = WebPushService(db)
    
    # Get subscription
    subscription_id = data.get("subscriptionId")
    if not subscription_id:
        raise HTTPException(status_code=400, detail="Missing subscriptionId")
    
    from repositories.subscription import SubscriptionRepository
    sub_repo = SubscriptionRepository(db)
    subscription = sub_repo.get(subscription_id)
    
    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")
    
    # Create a test notification
    notification = Notification(
        id=data.get("id", None),
        title=data.get("title", "Test Notification"),
        body=data.get("body", "This is a test notification"),
        icon_url=data.get("iconUrl"),
        badge_url=data.get("badgeUrl"),
        image_url=data.get("imageUrl"),
        action_url=data.get("actionUrl", "https://example.com"),
        actions=data.get("actions"),
        vibrate=data.get("vibrate"),
        require_interaction=data.get("requireInteraction", False),
        silent=data.get("silent", False),
        renotify=data.get("renotify", False),
        user_id=data.get("userId"),
        personalized_data=data.get("personalizedData", {}),
        time_to_live=data.get("timeToLive", 86400)
    )
    
    # Send the notification
    success = await web_push_service.send_notification(notification, subscription)
    
    return {"success": success}