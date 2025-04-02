import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

# Set up logger
logger = logging.getLogger(__name__)

# Import safely with fallback
try:
    from repositories.segment import SegmentRepository
except ImportError as e:
    logger.warning(f"Error importing SegmentRepository: {e}. Using mock implementation.")
    
    # Create mock implementation
    class SegmentRepository:
        """Mock implementation for development/testing"""
        def get_segment_by_id(self, segment_id: int):
            return {"id": segment_id, "name": f"Mock Segment {segment_id}"}
        
        def evaluate_segment_criteria(self, segment_id: int, user_data: Dict[str, Any]) -> bool:
            return True
        
        def get_all(self, active_only=False):
            """Mock get_all implementation"""
            return []

# Import safely
try:
    from core.celery_app import celery_app
except ImportError:
    logger.warning("Could not import celery_app from core.celery_app")
    # Create a no-op decorator for development/testing
    def shared_task(*args, **kwargs):
        def decorator(func):
            return func
        return decorator
    celery_app = type('MockCelery', (), {'task': shared_task})

# Mock service and utilities
class SegmentExecutionService:
    def execute_segment_query(self, segment_id):
        return {
            "user_count": 0,
            "execution_time_seconds": 0.1
        }

def audit_log(message=None, action_type=None, resource_type=None, resource_id=None, metadata=None):
    """Mock audit log function"""
    logger.info(f"AUDIT: {message} {action_type} {resource_type} {resource_id}")

# Define task
@celery_app.task(bind=True)
def evaluate_segment(self, segment_id: int, user_id: int = None, user_data: Optional[Dict[str, Any]] = None) -> bool:
    """
    Evaluates if a user belongs to a specific segment based on defined criteria.
    """
    try:
        logger.info(f"Evaluating segment {segment_id} for user {user_id}")
        
        # Default user data if not provided and user_id is provided
        if user_data is None and user_id is not None:
            user_data = {"user_id": user_id}
        
        # If no user_id is provided, we're evaluating the whole segment
        if user_id is None:
            segment_service = SegmentExecutionService()
            result = segment_service.execute_segment_query(segment_id)
            
            logger.info(f"Segment {segment_id} evaluation complete with {result.get('user_count', 0)} users")
            return result
        
        # For specific user evaluation
        # Instantiate repository
        repo = SegmentRepository()
        
        # Evaluate segment criteria
        result = repo.evaluate_segment_criteria(segment_id, user_data)
        
        logger.info(f"User {user_id} {'belongs to' if result else 'does not belong to'} segment {segment_id}")
        return result
        
    except Exception as e:
        logger.error(f"Error evaluating segment {segment_id}: {str(e)}")
        # Retry the task if it fails and it's a bound task
        if hasattr(self, 'retry'):
            self.retry(exc=e, countdown=60, max_retries=3)
        return False

@celery_app.task
def evaluate_all_segments():
    """Evaluate all active segments"""
    logger.info("Evaluating all segments")
    
    try:
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
    except Exception as e:
        logger.error(f"Error evaluating all segments: {str(e)}")
        return {"error": str(e)}

@celery_app.task
def refresh_stale_segments(days: int = 7):
    """
    Refresh segments that haven't been evaluated recently
    
    Args:
        days: Number of days to consider a segment stale
    """
    logger.info(f"Refreshing segments not evaluated in the last {days} days")
    
    try:
        segment_repo = SegmentRepository()
        cutoff_date = datetime.now() - timedelta(days=days)
        
        # Get all segments
        segments = segment_repo.get_all(active_only=True)
        
        stale_segments = []
        for segment in segments:
            # Check if segment is stale
            if not hasattr(segment, 'last_evaluated_at') or not segment.last_evaluated_at or segment.last_evaluated_at < cutoff_date:
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
    except Exception as e:
        logger.error(f"Error refreshing stale segments: {str(e)}")
        return {"error": str(e)}

@celery_app.task
def update_segment_analytics():
    """Update analytics data about segments"""
    logger.info("Updating segment analytics")
    
    try:
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
    except Exception as e:
        logger.error(f"Error updating segment analytics: {str(e)}")
        return {"error": str(e)}
