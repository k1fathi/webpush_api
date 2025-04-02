import logging
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from core.celery_app import celery_app
from models.domain.ab_test import AbTestModel
from models.domain.test_variant import TestVariantModel
from models.domain.notification import NotificationModel
from repositories.ab_test import AbTestRepository
from repositories.test_variant import TestVariantRepository
from repositories.notification import NotificationRepository
from services.ab_test import AbTestService

logger = logging.getLogger(__name__)

@celery_app.task
def check_ab_tests_completion():
    """Check for A/B tests that should be completed"""
    logger.info("Checking for A/B tests that should be completed")
    
    ab_test_repo = AbTestRepository()
    
    # Get active tests
    active_tests = ab_test_repo.get_active_tests()
    
    for test in active_tests:
        # Check if the test should be completed (e.g., has been running for a certain period)
        if test.start_date and (datetime.now() - test.start_date).days >= 7:  # Example: 7-day test duration
            logger.info(f"A/B test {test.id} has reached completion duration")
            
            # Mark as complete
            test.end_date = datetime.now()
            ab_test_repo.update(test.id, test)
            
            # Queue analysis task
            analyze_ab_test.delay(test.id)

@celery_app.task
def analyze_ab_test(ab_test_id: str):
    """Analyze the results of an A/B test"""
    logger.info(f"Analyzing A/B test {ab_test_id}")
    
    ab_test_service = AbTestService()
    
    try:
        # Get the test
        ab_test = ab_test_service.get_test(ab_test_id)
        if not ab_test:
            logger.error(f"A/B test {ab_test_id} not found")
            return
            
        # Analyze the results
        results = ab_test_service.analyze_results(ab_test_id)
        
        # If we have a significant winner, apply it automatically if needed
        winner_id = results.get("winner")
        is_significant = results.get("is_significant", False)
        
        if winner_id and is_significant:
            logger.info(f"Significant winner found for A/B test {ab_test_id}: variant {winner_id}")
            
            # Could automatically apply the winner
            # ab_test_service.apply_winning_variant(ab_test_id)
            
            # Or just log it for manual decision
            logger.info(f"Winning variant {winner_id} ready to be applied to campaign {ab_test.campaign_id}")
        else:
            logger.info(f"No significant winner found for A/B test {ab_test_id}")
            
    except Exception as e:
        logger.error(f"Error analyzing A/B test {ab_test_id}: {str(e)}")

@celery_app.task
def distribute_notifications(campaign_id: str, ab_test_id: str, user_ids: List[str]):
    """
    Distribute notifications across variants for an A/B test
    """
    logger.info(f"Distributing notifications for A/B test {ab_test_id}")
    
    test_variant_repo = TestVariantRepository()
    
    # Get the test variants
    variants = test_variant_repo.get_by_test(ab_test_id)
    if not variants:
        logger.error(f"No variants found for A/B test {ab_test_id}")
        return
        
    # Distribute users among variants
    # This is a simple random distribution; could be more sophisticated
    variant_assignments = {}
    for user_id in user_ids:
        # Select a variant (simple random distribution)
        variant = random.choice(variants)
        
        # Track assignments
        variant_assignments[user_id] = variant.id
        
        # Increment the sent counter for this variant
        test_variant_repo.increment_counters(variant.id, sent=1)
    
    # Return the assignments for further processing
    return variant_assignments

@celery_app.task
def track_variant_engagement(notification_id: str, event_type: str):
    """
    Track engagement events (open, click) for test variants
    """
    logger.info(f"Tracking {event_type} event for notification {notification_id}")
    
    notification_repo = NotificationRepository()
    test_variant_repo = TestVariantRepository()
    
    # Get the notification
    notification = notification_repo.get(notification_id)
    if not notification:
        logger.error(f"Notification {notification_id} not found")
        return
        
    # Find if this notification is part of an A/B test
    # This would require storing the variant ID with the notification
    # or looking up the relationship
    
    # This is a simplified example - you would need to implement the actual lookup
    variant_id = get_variant_for_notification(notification_id)
    if not variant_id:
        logger.info(f"Notification {notification_id} is not part of an A/B test")
        return
        
    # Update metrics based on event type
    if event_type == "open":
        test_variant_repo.increment_counters(variant_id, opened=1)
    elif event_type == "click":
        test_variant_repo.increment_counters(variant_id, clicked=1)

def get_variant_for_notification(notification_id: str) -> Optional[str]:
    """
    Helper function to get the variant ID for a notification
    This is a placeholder - you would need to implement the actual lookup
    """
    # This could involve querying a relationship table or metadata stored with the notification
    # For now, just return None as a placeholder
    return None
