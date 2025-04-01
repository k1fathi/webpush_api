import logging
from datetime import datetime
from typing import Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from pydantic import BaseModel

from api.deps import get_current_active_user
from core.exceptions.http import NotFoundException
from core.permissions.dependencies import has_permission
from models.domain.user import UserModel
from models.schemas.campaign import (
    CampaignCreate, 
    CampaignRead, 
    CampaignUpdate, 
    CampaignList,
    CampaignPreview,
    CampaignValidation
)
from services.campaign import CampaignService
from utils.audit import audit_log

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post(
    "/",
    response_model=CampaignRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(has_permission("create_campaign"))]
)
async def create_campaign(
    campaign: CampaignCreate,
    current_user: UserModel = Depends(get_current_active_user),
    campaign_service: CampaignService = Depends(),
):
    """Create a new campaign"""
    try:
        created_campaign = await campaign_service.create_campaign(campaign.dict())
        return created_campaign
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error creating campaign: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating campaign: {str(e)}"
        )

@router.get(
    "/",
    response_model=CampaignList,
    dependencies=[Depends(has_permission("list_campaigns"))]
)
async def list_campaigns(
    skip: int = 0,
    limit: int = 100,
    campaign_service: CampaignService = Depends(),
):
    """List all campaigns with pagination"""
    try:
        campaigns = await campaign_service.get_all_campaigns(skip=skip, limit=limit)
        total = await campaign_service.campaign_repo.count_campaigns()
        return {
            "items": campaigns,
            "total": total,
            "skip": skip,
            "limit": limit
        }
    except Exception as e:
        logger.error(f"Error listing campaigns: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error listing campaigns: {str(e)}"
        )

@router.get(
    "/{campaign_id}",
    response_model=CampaignRead,
    dependencies=[Depends(has_permission("read_campaign"))]
)
async def get_campaign(
    campaign_id: str = Path(...),
    campaign_service: CampaignService = Depends(),
):
    """Get a campaign by ID"""
    campaign = await campaign_service.get_campaign(campaign_id)
    if not campaign:
        raise NotFoundException("Campaign not found")
    return campaign

@router.put(
    "/{campaign_id}",
    response_model=CampaignRead,
    dependencies=[Depends(has_permission("update_campaign"))]
)
async def update_campaign(
    campaign_id: str,
    campaign: CampaignUpdate,
    current_user: UserModel = Depends(get_current_active_user),
    campaign_service: CampaignService = Depends(),
):
    """Update a campaign"""
    try:
        updated_campaign = await campaign_service.update_campaign(campaign_id, campaign.dict(exclude_unset=True))
        return updated_campaign
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error updating campaign: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating campaign: {str(e)}"
        )

@router.delete(
    "/{campaign_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(has_permission("delete_campaign"))]
)
async def delete_campaign(
    campaign_id: str = Path(...),
    current_user: UserModel = Depends(get_current_active_user),
    campaign_service: CampaignService = Depends(),
):
    """Delete a campaign"""
    try:
        result = await campaign_service.delete_campaign(campaign_id)
        if not result:
            raise NotFoundException("Campaign not found")
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except NotFoundException:
        raise
    except Exception as e:
        logger.error(f"Error deleting campaign: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting campaign: {str(e)}"
        )

@router.post(
    "/{campaign_id}/template/{template_id}",
    response_model=CampaignRead,
    dependencies=[Depends(has_permission("update_campaign"))]
)
async def set_campaign_template(
    campaign_id: str,
    template_id: str,
    current_user: UserModel = Depends(get_current_active_user),
    campaign_service: CampaignService = Depends(),
):
    """Set the template for a campaign"""
    try:
        updated_campaign = await campaign_service.set_campaign_template(campaign_id, template_id)
        return updated_campaign
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error setting campaign template: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error setting campaign template: {str(e)}"
        )

@router.post(
    "/{campaign_id}/segment/{segment_id}",
    response_model=CampaignRead,
    dependencies=[Depends(has_permission("update_campaign"))]
)
async def set_campaign_segment(
    campaign_id: str,
    segment_id: str,
    current_user: UserModel = Depends(get_current_active_user),
    campaign_service: CampaignService = Depends(),
):
    """Set the target segment for a campaign"""
    try:
        updated_campaign = await campaign_service.set_campaign_segment(campaign_id, segment_id)
        return updated_campaign
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error setting campaign segment: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error setting campaign segment: {str(e)}"
        )

@router.post(
    "/{campaign_id}/schedule",
    response_model=CampaignRead,
    dependencies=[Depends(has_permission("publish_campaign"))]
)
async def schedule_campaign(
    campaign_id: str,
    scheduled_time: datetime,
    current_user: UserModel = Depends(get_current_active_user),
    campaign_service: CampaignService = Depends(),
):
    """Schedule a campaign for delivery"""
    try:
        updated_campaign = await campaign_service.schedule_campaign(campaign_id, scheduled_time)
        return updated_campaign
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error scheduling campaign: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error scheduling campaign: {str(e)}"
        )

@router.post(
    "/{campaign_id}/validate",
    response_model=CampaignValidation,
    dependencies=[Depends(has_permission("read_campaign"))]
)
async def validate_campaign(
    campaign_id: str,
    campaign_service: CampaignService = Depends(),
):
    """Validate a campaign before scheduling"""
    try:
        validation_result = await campaign_service.validate_campaign(campaign_id)
        return validation_result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error validating campaign: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error validating campaign: {str(e)}"
        )

@router.post(
    "/{campaign_id}/preview",
    response_model=CampaignPreview,
    dependencies=[Depends(has_permission("read_campaign"))]
)
async def preview_campaign(
    campaign_id: str,
    user_id: Optional[str] = None,
    campaign_service: CampaignService = Depends(),
):
    """Generate a preview of the campaign"""
    try:
        preview = await campaign_service.preview_campaign(campaign_id, user_id)
        return preview
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error generating campaign preview: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating campaign preview: {str(e)}"
        )

@router.post(
    "/{campaign_id}/approve",
    response_model=CampaignRead,
    dependencies=[Depends(has_permission("approve_campaign"))]
)
async def approve_campaign(
    campaign_id: str,
    current_user: UserModel = Depends(get_current_active_user),
    campaign_service: CampaignService = Depends(),
):
    """Approve a campaign that was submitted for approval"""
    try:
        approved_campaign = await campaign_service.approve_campaign(campaign_id)
        return approved_campaign
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error approving campaign: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error approving campaign: {str(e)}"
        )

@router.post(
    "/{campaign_id}/reject",
    response_model=CampaignRead,
    dependencies=[Depends(has_permission("approve_campaign"))]
)
async def reject_campaign(
    campaign_id: str,
    reason: Optional[str] = None,
    current_user: UserModel = Depends(get_current_active_user),
    campaign_service: CampaignService = Depends(),
):
    """Reject a campaign that was submitted for approval"""
    try:
        rejected_campaign = await campaign_service.reject_campaign(campaign_id, reason)
        return rejected_campaign
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error rejecting campaign: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error rejecting campaign: {str(e)}"
        )

@router.post(
    "/{campaign_id}/submit-for-approval",
    response_model=CampaignRead,
    dependencies=[Depends(has_permission("update_campaign"))]
)
async def submit_for_approval(
    campaign_id: str,
    current_user: UserModel = Depends(get_current_active_user),
    campaign_service: CampaignService = Depends(),
):
    """Submit a campaign for approval"""
    try:
        submitted_campaign = await campaign_service.submit_for_approval(campaign_id)
        return submitted_campaign
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error submitting campaign for approval: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error submitting campaign for approval: {str(e)}"
        )

@router.post(
    "/{campaign_id}/activate",
    response_model=CampaignRead,
    dependencies=[Depends(has_permission("publish_campaign"))]
)
async def activate_campaign(
    campaign_id: str,
    current_user: UserModel = Depends(get_current_active_user),
    campaign_service: CampaignService = Depends(),
):
    """Activate a campaign for immediate sending"""
    try:
        activated_campaign = await campaign_service.activate_campaign(campaign_id)
        return activated_campaign
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error activating campaign: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error activating campaign: {str(e)}"
        )

@router.post(
    "/{campaign_id}/pause",
    response_model=CampaignRead,
    dependencies=[Depends(has_permission("publish_campaign"))]
)
async def pause_campaign(
    campaign_id: str,
    current_user: UserModel = Depends(get_current_active_user),
    campaign_service: CampaignService = Depends(),
):
    """Pause a running campaign"""
    try:
        paused_campaign = await campaign_service.pause_campaign(campaign_id)
        return paused_campaign
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error pausing campaign: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error pausing campaign: {str(e)}"
        )

@router.post(
    "/{campaign_id}/resume",
    response_model=CampaignRead,
    dependencies=[Depends(has_permission("publish_campaign"))]
)
async def resume_campaign(
    campaign_id: str,
    current_user: UserModel = Depends(get_current_active_user),
    campaign_service: CampaignService = Depends(),
):
    """Resume a paused campaign"""
    try:
        resumed_campaign = await campaign_service.resume_campaign(campaign_id)
        return resumed_campaign
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error resuming campaign: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error resuming campaign: {str(e)}"
        )

@router.get(
    "/{campaign_id}/stats",
    dependencies=[Depends(has_permission("read_analytics"))]
)
async def get_campaign_stats(
    campaign_id: str,
    campaign_service: CampaignService = Depends(),
):
    """Get statistics for a campaign"""
    try:
        stats = await campaign_service.get_campaign_stats(campaign_id)
        return stats
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error getting campaign stats: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting campaign stats: {str(e)}"
        )
