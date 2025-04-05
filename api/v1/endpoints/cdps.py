import logging
from typing import Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Path, status
from fastapi.responses import JSONResponse

from api.deps import get_current_active_user
from core.exceptions.http import NotFoundException
from core.permissions.dependencies import has_permission
from models.domain.user import UserModel
from models.schemas.cdp_integration import CdpIntegration, CdpIntegrationRead, CdpIntegrationUpdate
from services.cdp import CdpService
from utils.audit import audit_log

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get(
    "/status",
    dependencies=[Depends(has_permission("read_cdp_integration"))]
)
async def get_cdp_status(
    cdp_service: CdpService = Depends(),
):
    """Get status of CDP integration"""
    return {
        "is_enabled": cdp_service.is_enabled(),
        "is_available": cdp_service.is_available,
        "api_url": cdp_service.api_url if cdp_service.is_enabled() else None,
    }

@router.get(
    "/user/{user_id}",
    response_model=CdpIntegrationRead,
    dependencies=[Depends(has_permission("read_cdp_integration"))]
)
async def get_user_cdp_integration(
    user_id: str = Path(...),
    cdp_service: CdpService = Depends(),
):
    """Get CDP integration data for a specific user"""
    cdp_integration = await cdp_service.cdp_repo.get_by_user_id(user_id)
    if not cdp_integration:
        raise NotFoundException("CDP integration not found for this user")
    return cdp_integration

@router.post(
    "/sync/user/{user_id}",
    dependencies=[Depends(has_permission("update_cdp_integration"))]
)
async def sync_user_with_cdp(
    user_id: str = Path(...),
    cdp_service: CdpService = Depends(),
    current_user: UserModel = Depends(get_current_active_user),
):
    """Manually sync a user with the CDP"""
    if not cdp_service.is_enabled():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="CDP integration is not enabled"
        )
    
    result = await cdp_service.sync_user_data(user_id)
    
    if result:
        audit_log(
            f"Manual CDP sync requested by {current_user.id} for user {user_id}",
            action_type="cdp_sync", 
            user_id=str(current_user.id)
        )
        return {"status": "success", "message": "User data synced with CDP"}
    else:
        return {
            "status": "error", 
            "message": "Failed to sync user data. See logs for details."
        }

@router.post(
    "/track-event",
    dependencies=[Depends(has_permission("update_cdp_integration"))]
)
async def track_cdp_event(
    event_data: Dict,
    cdp_service: CdpService = Depends(),
):
    """Track an event in the CDP"""
    if not cdp_service.is_enabled():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="CDP integration is not enabled"
        )
    
    if "user_id" not in event_data or "event_type" not in event_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Event must include 'user_id' and 'event_type'"
        )
    
    result = await cdp_service.track_event(event_data)
    
    if result:
        return {"status": "success", "message": "Event tracked in CDP"}
    else:
        return {
            "status": "error", 
            "message": "Failed to track event. See logs for details."
        }

@router.get(
    "/recent-syncs",
    dependencies=[Depends(has_permission("read_cdp_integration"))]
)
async def get_recent_cdp_syncs(
    limit: int = 20,
    cdp_service: CdpService = Depends(),
):
    """Get recent CDP sync operations"""
    syncs = await cdp_service.cdp_repo.get_recent_syncs(limit)
    return {
        "count": len(syncs),
        "syncs": [
            {
                "user_id": str(sync.user_id),
                "sync_status": sync.sync_status,
                "last_synced": sync.last_synced,
                "error_message": sync.error_message
            }
            for sync in syncs
        ]
    }
