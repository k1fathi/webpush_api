import logging
from typing import Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from fastapi.responses import JSONResponse

from api.deps import get_current_active_user
from core.exceptions.http import NotFoundException
from core.permissions.dependencies import has_permission
from models.domain.user import UserModel
from services.segment_execution import SegmentExecutionService
from utils.audit import audit_log

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post(
    "/{segment_id}/execute",
    dependencies=[Depends(has_permission("execute_segment"))]
)
async def execute_segment(
    segment_id: str = Path(...),
    include_users: bool = Query(False, description="Whether to include matching user IDs in the response"),
    segment_execution_service: SegmentExecutionService = Depends(),
    current_user: UserModel = Depends(get_current_active_user),
):
    """Execute a segment query to find matching users"""
    try:
        result = await segment_execution_service.execute_segment_query(
            segment_id=segment_id,
            get_user_ids=include_users
        )
        
        # Audit the execution request
        audit_log(
            message=f"Segment execution requested by user",
            user_id=str(current_user.id),
            action_type="segment_execute",
            resource_type="segment",
            resource_id=segment_id
        )
        
        return result
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except NotFoundException:
        raise
    except Exception as e:
        logger.error(f"Error executing segment {segment_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error executing segment: {str(e)}"
        )

@router.get(
    "/{segment_id}/preview",
    dependencies=[Depends(has_permission("read_segment"))]
)
async def preview_segment(
    segment_id: str = Path(...),
    limit: int = Query(10, ge=1, le=100, description="Maximum number of matching users to return"),
    segment_execution_service: SegmentExecutionService = Depends(),
    current_user: UserModel = Depends(get_current_active_user),
):
    """Preview the results of a segment query with a limited number of users"""
    try:
        # Execute the segment to get matching users
        result = await segment_execution_service.execute_segment_query(
            segment_id=segment_id,
            get_user_ids=True
        )
        
        # Limit the number of user IDs returned
        if "user_ids" in result:
            result["user_ids"] = result["user_ids"][:limit]
            result["preview_limit"] = limit
            result["is_preview"] = True
        
        return result
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except NotFoundException:
        raise
    except Exception as e:
        logger.error(f"Error previewing segment {segment_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error previewing segment: {str(e)}"
        )

@router.post(
    "/batch-execute",
    dependencies=[Depends(has_permission("execute_segment"))]
)
async def batch_execute_segments(
    segment_ids: List[str],
    segment_execution_service: SegmentExecutionService = Depends(),
    current_user: UserModel = Depends(get_current_active_user),
):
    """Execute multiple segment queries in batch"""
    results = []
    errors = []
    
    for segment_id in segment_ids:
        try:
            result = await segment_execution_service.execute_segment_query(segment_id)
            results.append(result)
        except Exception as e:
            errors.append({
                "segment_id": segment_id,
                "error": str(e)
            })
    
    return {
        "successful_executions": results,
        "failed_executions": errors,
        "total_segments": len(segment_ids),
        "success_count": len(results),
        "error_count": len(errors)
    }
