import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from core.celery_app import celery_app
from models.cep_decision import DecisionStatus
from repositories.cep_decision import CepDecisionRepository
from repositories.notification import NotificationRepository
from repositories.user import UserRepository
from services.cep import CepService

logger = logging.getLogger(__name__)

@celery_app.task
def analyze_decision_performance():
    """Analyze the performance of channel decisions"""
    logger.info("Analyzing CEP decision performance")
    
    cep_repo = CepDecisionRepository()
    
    # Get recent completed decisions
    completed_decisions = cep_repo.get_by_status(DecisionStatus.COMPLETED)
    
    if not completed_decisions:
        logger.info("No completed decisions to analyze")
        return
        
    # Group decisions by channel
    channels = {}
    for decision in completed_decisions:
        channel = decision.selected_channel
        if channel not in channels:
            channels[channel] = {
                "total": 0,
                "engaged": 0,
                "conversion": 0
            }
            
        channels[channel]["total"] += 1
        
        # Check outcome
        if decision.outcome:
            if decision.outcome.get("engaged"):
                channels[channel]["engaged"] += 1
            if decision.outcome.get("conversion"):
                channels[channel]["conversion"] += 1
    
    # Calculate effectiveness
    for channel, stats in channels.items():
        total = stats["total"]
        if total > 0:
            engagement_rate = stats["engaged"] / total
            conversion_rate = stats["conversion"] / total if stats["engaged"] > 0 else 0
            
            logger.info(
                f"Channel {channel}: {total} decisions, "
                f"{engagement_rate:.1%} engagement, "
                f"{conversion_rate:.1%} conversion"
            )
    
    # TODO: Use this data to update channel weights or other decision parameters

@celery_app.task
def track_decision_outcome(notification_id: str, outcome_type: str):
    """Track the outcome of a channel decision"""
    logger.info(f"Tracking decision outcome for notification {notification_id}: {outcome_type}")
    
    # Repositories
    notification_repo = NotificationRepository()
    cep_repo = CepDecisionRepository()
    
    # Get the notification
    notification = notification_repo.get(notification_id)
    if not notification:
        logger.error(f"Notification {notification_id} not found")
        return
        
    # Find the decision associated with this notification
    # In a real implementation, you would have a direct link from notification to decision
    # This is a simplified version that assumes recent decisions for this user
    user_decisions = cep_repo.get_by_user(notification.user_id, limit=10)
    
    # Find the most recent decision before this notification was sent
    relevant_decision = None
    for decision in user_decisions:
        if decision.decision_time <= notification.sent_at:
            relevant_decision = decision
            break
    
    if not relevant_decision:
        logger.warning(f"No relevant decision found for notification {notification_id}")
        return
    
    # Update the decision outcome
    outcome_data = {
        "notification_id": notification_id,
        "outcome_type": outcome_type,
        "timestamp": datetime.now().isoformat()
    }
    
    if outcome_type == "delivered":
        outcome_data["delivered"] = True
    elif outcome_type == "opened":
        outcome_data["delivered"] = True
        outcome_data["engaged"] = True
        outcome_data["time_to_engagement"] = (
            notification.opened_at - notification.delivered_at
        ).total_seconds() if notification.opened_at and notification.delivered_at else None
    elif outcome_type == "clicked":
        outcome_data["delivered"] = True
        outcome_data["engaged"] = True
        outcome_data["strong_engagement"] = True
        outcome_data["time_to_engagement"] = (
            notification.clicked_at - notification.delivered_at
        ).total_seconds() if notification.clicked_at and notification.delivered_at else None
    elif outcome_type == "conversion":
        outcome_data["delivered"] = True
        outcome_data["engaged"] = True
        outcome_data["conversion"] = True
    
    # Update the decision with this outcome
    cep_service = CepService()
    cep_service.record_decision_outcome(
        decision_id=relevant_decision.id,
        outcome=outcome_data
    )

@celery_app.task
def update_channel_effectiveness():
    """Update channel effectiveness ratings based on recent performance"""
    logger.info("Updating channel effectiveness ratings")
    
    cep_repo = CepDecisionRepository()
    
    # Get decisions with outcomes from last 30 days
    recent_decisions = cep_repo.get_recent_decisions(days=30)
    
    # Group by channel and calculate effectiveness
    channel_stats = {}
    for decision in recent_decisions:
        channel = decision.selected_channel
        if channel not in channel_stats:
            channel_stats[channel] = {
                "total": 0,
                "engaged": 0,
                "converted": 0
            }
            
        channel_stats[channel]["total"] += 1
        
        if decision.outcome:
            if decision.outcome.get("engaged"):
                channel_stats[channel]["engaged"] += 1
            if decision.outcome.get("conversion"):
                channel_stats[channel]["converted"] += 1
    
    # Calculate effectiveness scores
    effectiveness_scores = {}
    for channel, stats in channel_stats.items():
        if stats["total"] >= 10:  # Only score channels with enough data
            # Weighted score: engagement is good, conversion is better
            engagement_rate = stats["engaged"] / stats["total"] if stats["total"] > 0 else 0
            conversion_rate = stats["converted"] / stats["total"] if stats["total"] > 0 else 0
            
            # Weight conversion 3x more than engagement
            effectiveness_scores[channel] = (engagement_rate + (conversion_rate * 3)) / 4
    
    logger.info(f"Updated channel effectiveness scores: {effectiveness_scores}")
    
    # TODO: Store these scores somewhere they can be used by the CEP service
    # This would typically be in a database table or cache

@celery_app.task
def optimize_decision_parameters():
    """Optimize decision parameters based on performance data"""
    logger.info("Optimizing CEP decision parameters")
    
    # This would be a more complex task that analyzes decision performance
    # and adjusts the parameters used in the decision algorithm
    
    # For example:
    # - Update time-of-day factors based on when users engage most
    # - Adjust content type weights based on what generates most engagement
    # - Modify urgency thresholds based on observed response times
    
    # This is a placeholder for a real implementation
    pass
