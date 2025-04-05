import logging
from datetime import datetime
from typing import Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from fastapi.responses import JSONResponse

from api.deps import get_current_active_user
from core.exceptions.http import NotFoundException
from core.permissions.dependencies import has_permission
from models.domain.user import UserModel
from models.schemas.segment import (
    SegmentCreate,
    SegmentRead,
    SegmentUpdate,
    SegmentList,
    SegmentEvaluation,
    SegmentUserBatch,
    SegmentStats,
    SegmentType
)
from services.segment import SegmentService
from utils.audit import audit_log

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post(
    "/",
    response_model=SegmentRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(has_permission("create_segment"))]
)
async def create_segment(
    segment: SegmentCreate,
    current_user: UserModel = Depends(get_current_active_user),
    segment_service: SegmentService = Depends(),
):
    """Create a new segment"""
    try:
        created = await segment_service.create_segment(segment.dict())
        return created
    except Exception as e:
        logger.error(f"Error creating segment: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating segment: {str(e)}"
        )

@router.get(
    "/",
    response_model=SegmentList,
    dependencies=[Depends(has_permission("list_segments"))]
)
async def list_segments(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    active_only: bool = Query(False),
    segment_service: SegmentService = Depends(),
):
    """List all segments with pagination"""
    try:
        segments, total = await segment_service.get_all_segments(skip, limit, active_only)
        return {
            "items": segments,
            "total": total,
            "skip": skip,
            "limit": limit
        }
    except Exception as e:
        logger.error(f"Error listing segments: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error listing segments: {str(e)}"
        )

@router.get(
    "/{segment_id}",
    response_model=SegmentRead,
    dependencies=[Depends(has_permission("read_segment"))]
)
async def get_segment(
    segment_id: str = Path(...),
    segment_service: SegmentService = Depends(),
):
    """Get a segment by ID"""
    segment = await segment_service.get_segment(segment_id)
    if not segment:
        raise NotFoundException("Segment not found")
    return segment

@router.put(
    "/{segment_id}",
    response_model=SegmentRead,
    dependencies=[Depends(has_permission("update_segment"))]
)
async def update_segment(
    segment_id: str,
    segment: SegmentUpdate,
    current_user: UserModel = Depends(get_current_active_user),
    segment_service: SegmentService = Depends(),
):
    """Update a segment"""
    try:
        updated_segment = await segment_service.update_segment(
            segment_id, segment.dict(exclude_unset=True)
        )
        return updated_segment
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error updating segment: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating segment: {str(e)}"
        )

@router.delete(
    "/{segment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(has_permission("delete_segment"))]
)
async def delete_segment(
    segment_id: str = Path(...),
    current_user: UserModel = Depends(get_current_active_user),
    segment_service: SegmentService = Depends(),
):
    """Delete a segment"""
    try:
        result = await segment_service.delete_segment(segment_id)
        if not result:
            raise NotFoundException("Segment not found")
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except NotFoundException:
        raise
    except Exception as e:
        logger.error(f"Error deleting segment: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting segment: {str(e)}"
        )

@router.post(
    "/{segment_id}/evaluate",
    response_model=SegmentEvaluation,
    dependencies=[Depends(has_permission("evaluate_segment"))]
)
async def evaluate_segment(
    segment_id: str,
    get_matched_users: bool = Query(False),
    segment_service: SegmentService = Depends(),
):
    """Evaluate a segment to determine matching users"""
    try:
        result = await segment_service.evaluate_segment(
            segment_id, get_matched_users=get_matched_users
        )
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error evaluating segment: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error evaluating segment: {str(e)}"
        )

@router.post(
    "/{segment_id}/users/add",
    dependencies=[Depends(has_permission("update_segment"))]
)
async def add_users_to_segment(
    segment_id: str,
    user_batch: SegmentUserBatch,
    segment_service: SegmentService = Depends(),
):
    """Add users to a static segment"""
    try:
        result = await segment_service.add_users_to_static_segment(
            segment_id, user_batch.user_ids
        )
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error adding users to segment: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error adding users to segment: {str(e)}"
        )

@router.post(
    "/{segment_id}/users/remove",
    dependencies=[Depends(has_permission("update_segment"))]
)
async def remove_users_from_segment(
    segment_id: str,
    user_batch: SegmentUserBatch,
    segment_service: SegmentService = Depends(),
):
    """Remove users from a static segment"""
    try:
        result = await segment_service.remove_users_from_static_segment(
            segment_id, user_batch.user_ids
        )
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error removing users from segment: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error removing users from segment: {str(e)}"
        )

@router.get(
    "/{segment_id}/stats",
    response_model=SegmentStats,
    dependencies=[Depends(has_permission("read_segment"))]
)
async def get_segment_stats(
    segment_id: str = Path(...),
    segment_service: SegmentService = Depends(),
):
    """Get statistics for a segment"""
    try:
        stats = await segment_service.get_segment_stats(segment_id)
        return stats
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error getting segment stats: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting segment stats: {str(e)}"
        )

@router.get(
    "/search",
    response_model=List[SegmentRead],
    dependencies=[Depends(has_permission("list_segments"))]
)
async def search_segments(
    query: str = Query(..., min_length=1),
    limit: int = Query(10, ge=1, le=50),
    segment_service: SegmentService = Depends(),
):
    """Search for segments by name or description"""
    try:
        segments = await segment_service.search_segments(query, limit)
        return segments
    except Exception as e:
        logger.error(f"Error searching segments: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error searching segments: {str(e)}"
        )
