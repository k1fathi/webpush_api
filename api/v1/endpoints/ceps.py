import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status

from api.deps import get_current_active_user
from core.exceptions.http import NotFoundException
from core.permissions.dependencies import has_permission
from models.domain.user import UserModel
from models.cep_decision import CepDecisionCreate, CepDecisionRead, DecisionStatus
from services.cep import CepService
from utils.audit import audit_log

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get(
    "/channel-decision/{user_id}",
    dependencies=[Depends(has_permission("read_cep_decision"))]
)
async def get_optimal_channel(
    user_id: str = Path(...),
    campaign_id: Optional[str] = Query(None),
    message_type: Optional[str] = Query(None),
    cep_service: CepService = Depends(),
):
    """Get the optimal channel for a user"""
    try:
        message_data = {"type": message_type} if message_type else None
        optimal_channel = await cep_service.get_optimal_channel(
            user_id=user_id,
            campaign_id=campaign_id,
            message_data=message_data
        )
        return {
            "user_id": user_id,
            "selected_channel": optimal_channel,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error determining optimal channel: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error determining optimal channel: {str(e)}"
        )

@router.get(
    "/optimal-time/{user_id}",
    dependencies=[Depends(has_permission("read_cep_decision"))]
)
async def get_optimal_send_time(
    user_id: str = Path(...),
    channel: str = Query("webpush"),
    max_delay_hours: int = Query(24),
    cep_service: CepService = Depends(),
):
    """Get the optimal send time for a notification"""
    try:
        optimal_time = await cep_service.get_optimal_send_time(
            user_id=user_id,
            channel=channel,
            max_delay_hours=max_delay_hours
        )
        return {
            "user_id": user_id,
            "channel": channel,
            "optimal_time": optimal_time.isoformat(),
            "delay_seconds": (optimal_time - datetime.now()).total_seconds()
        }
    except Exception as e:
        logger.error(f"Error determining optimal send time: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error determining optimal send time: {str(e)}"
        )

@router.post(
    "/optimize-notification",
    dependencies=[Depends(has_permission("update_cep_decision"))]
)
async def optimize_notification_parameters(
    user_id: str,
    notification_data: Dict,
    cep_service: CepService = Depends(),
):
    """Optimize notification parameters for a user"""
    try:
        optimized_data = await cep_service.optimize_notification_parameters(
            user_id=user_id,
            notification_data=notification_data
        )
        return optimized_data
    except Exception as e:
        logger.error(f"Error optimizing notification parameters: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error optimizing notification parameters: {str(e)}"
        )

@router.post(
    "/record-decision",
    response_model=CepDecisionRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(has_permission("create_cep_decision"))]
)
async def record_channel_decision(
    decision: CepDecisionCreate,
    current_user: UserModel = Depends(get_current_active_user),
    cep_service: CepService = Depends(),
):
    """Record a channel selection decision"""
    try:
        created_decision = await cep_service.record_channel_decision(
            user_id=decision.user_id,
            campaign_id=decision.campaign_id,
            selected_channel=decision.selected_channel,
            score=decision.score,
            factors=decision.decision_factors
        )
        return created_decision
    except Exception as e:
        logger.error(f"Error recording channel decision: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error recording channel decision: {str(e)}"
        )

@router.post(
    "/record-outcome/{decision_id}",
    response_model=CepDecisionRead,
    dependencies=[Depends(has_permission("update_cep_decision"))]
)
async def record_decision_outcome(
    decision_id: str = Path(...),
    outcome: Dict = None,
    cep_service: CepService = Depends(),
):
    """Record the outcome of a channel decision"""
    try:
        updated_decision = await cep_service.record_decision_outcome(
            decision_id=decision_id,
            outcome=outcome or {}
        )
        if not updated_decision:
            raise NotFoundException("Decision not found")
        return updated_decision
    except NotFoundException:
        raise
    except Exception as e:
        logger.error(f"Error recording decision outcome: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error recording decision outcome: {str(e)}"
        )

@router.get(
    "/decisions/{user_id}",
    response_model=List[CepDecisionRead],
    dependencies=[Depends(has_permission("read_cep_decision"))]
)
async def get_user_decisions(
    user_id: str = Path(...),
    limit: int = Query(20, ge=1, le=100),
    cep_service: CepService = Depends(),
):
    """Get CEP decisions for a user"""
    try:
        decisions = await cep_service.cep_repo.get_by_user(user_id, limit=limit)
        return decisions
    except Exception as e:
        logger.error(f"Error getting user decisions: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting user decisions: {str(e)}"
        )

@router.get(
    "/statistics",
    dependencies=[Depends(has_permission("read_cep_decision"))]
)
async def get_decision_statistics(
    days: int = Query(30, ge=1, le=365),
    cep_service: CepService = Depends(),
):
    """Get statistics about CEP decisions"""
    try:
        # Get channel decision counts
        channel_counts = await cep_service.cep_repo.get_channel_decision_counts(days=days)
        
        # Get total decisions
        total = sum(channel_counts.values())
        
        # Calculate percentages
        channel_percentages = {
            channel: (count / total * 100 if total > 0 else 0) 
            for channel, count in channel_counts.items()
        }
        
        return {
            "period": f"Last {days} days",
            "total_decisions": total,
            "channel_counts": channel_counts,
            "channel_percentages": channel_percentages
        }
    except Exception as e:
        logger.error(f"Error getting decision statistics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting decision statistics: {str(e)}"
        )
