import logging
from datetime import datetime, timedelta
from typing import Dict, List

from core.celery_app import celery_app
from repositories.segment import SegmentRepository
from services.segment_execution import SegmentExecutionService
from utils.audit import audit_log

logger = logging.getLogger(__name__)

@celery_app.task
def evaluate_segment(segment_id: str):
    """
    Evaluate a segment to determine matching users
    
    Args:
        segment_id: The segment ID to evaluate
    """
    logger.info(f"Evaluating segment {segment_id}")
    
    segment_execution_service = SegmentExecutionService()
    
    try:
        # Execute the segment using the execution service
        result = segment_execution_service.execute_segment_query(segment_id)
        
        logger.info(f"Segment {segment_id} evaluation complete with {result['user_count']} users")
        
        # Log the completion
        audit_log(
            message=f"Segment evaluation task completed",
            action_type="evaluate_segment_task",
            resource_type="segment",
            resource_id=segment_id,
            metadata={
                "user_count": result["user_count"],
                "execution_time": result["execution_time_seconds"]
            }
        )
        
        return result
    except Exception as e:
        logger.error(f"Error evaluating segment {segment_id}: {str(e)}")
        
        # Log the failure
        audit_log(
            message=f"Segment evaluation task failed",
            action_type="evaluate_segment_task_failed",
            resource_type="segment",
            resource_id=segment_id,
            metadata={"error": str(e)}
        )
        
        raise

@celery_app.task
def evaluate_all_segments():
    """Evaluate all active segments"""
    logger.info("Evaluating all segments")
    
    segment_repo = SegmentRepository()
    
    # Get all active segments
    segments = segment_repo.get_all(active_only=True)
    
    if not segments:
        logger.info("No active segments to evaluate")
        return {"segments_evaluated": 0}
        
    logger.info(f"Found {len(segments)} active segments to evaluate")
    
    # Queue individual segment evaluations
    for segment in segments:
        evaluate_segment.delay(str(segment.id))
    
    # Log the batch evaluation
    audit_log(
        message=f"Queued evaluation for {len(segments)} segments",
        action_type="evaluate_all_segments",
        metadata={"segment_count": len(segments)}
    )
    
    return {
        "segments_queued": len(segments),
        "timestamp": datetime.now().isoformat()
    }

@celery_app.task
def refresh_stale_segments(days: int = 7):
    """
    Refresh segments that haven't been evaluated recently
    
    Args:
        days: Number of days to consider a segment stale
    """
    logger.info(f"Refreshing segments not evaluated in the last {days} days")
    
    segment_repo = SegmentRepository()
    cutoff_date = datetime.now() - timedelta(days=days)
    
    # Get all segments
    segments = segment_repo.get_all(active_only=True)
    
    stale_segments = []
    for segment in segments:
        # Check if segment is stale
        if not segment.last_evaluated_at or segment.last_evaluated_at < cutoff_date:
            stale_segments.append(segment)
            # Queue evaluation
            evaluate_segment.delay(str(segment.id))
    
    # Log the stale segment refresh
    audit_log(
        message=f"Queued refresh for {len(stale_segments)} stale segments",
        action_type="refresh_stale_segments",
        metadata={
            "stale_segments": len(stale_segments),
            "total_segments": len(segments),
            "stale_threshold_days": days
        }
    )
    
    logger.info(f"Queued {len(stale_segments)} stale segments for refresh")
    return {
        "stale_segments": len(stale_segments),
        "total_segments": len(segments)
    }

@celery_app.task
def update_segment_analytics():
    """Update analytics data about segments"""
    logger.info("Updating segment analytics")
    
    # This task would update analytics data about segments
    # such as growth rates, usage patterns, etc.
    
    # This is a placeholder for a more complex implementation
    segment_repo = SegmentRepository()
    segments = segment_repo.get_all()
    
    # Example analytics we might calculate:
    # - Growth rate (change in user count over time)
    # - Usage in campaigns
    # - Performance impact
    
    logger.info(f"Updated analytics for {len(segments)} segments")
    return {
        "segments_analyzed": len(segments),
        "timestamp": datetime.now().isoformat()
    }
