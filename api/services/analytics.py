from sqlalchemy.orm import Session
from typing import List, Dict, Any
from datetime import datetime, timedelta
from core.models import Campaign, Notification, DeliveryStatus, NotificationSegment
from api.schemas import ABTestCreate

async def get_campaign_metrics(campaign_id: str, metrics: List[str], db: Session) -> Dict[str, float]:
    """Calculate campaign performance metrics"""
    result = {}
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    
    if "delivery_rate" in metrics:
        total = db.query(DeliveryStatus).filter(
            DeliveryStatus.notification_id.in_([n.id for n in campaign.notifications])
        ).count()
        delivered = db.query(DeliveryStatus).filter(
            DeliveryStatus.status == "delivered"
        ).count()
        result["delivery_rate"] = (delivered / total * 100) if total > 0 else 0
    
    # Add more metric calculations
    return result

async def get_segment_metrics(date_range: str, db: Session) -> Dict[str, Dict[str, float]]:
    """Calculate performance metrics per segment"""
    segments = {}
    end_date = datetime.utcnow()
    
    if date_range == "last_7_days":
        start_date = end_date - timedelta(days=7)
    else:
        start_date = end_date - timedelta(days=30)
    
    # Calculate metrics for each segment
    segment_stats = db.query(NotificationSegment).all()
    for segment in segment_stats:
        metrics = calculate_segment_performance(segment, start_date, end_date, db)
        segments[segment.segment_name] = metrics
    
    return segments

def calculate_segment_performance(segment, start_date, end_date, db):
    """Calculate detailed performance metrics for a segment"""
    # Implementation here
    pass

async def create_ab_test(test: ABTestCreate, db: Session) -> Dict[str, Any]:
    """Create and initialize an A/B test for a campaign"""
    try:
        campaign = db.query(Campaign).filter(Campaign.id == test.campaign_id).first()
        if not campaign:
            raise ValueError(f"Campaign {test.campaign_id} not found")
        
        # Create variant notifications
        for variant in test.variants:
            notification = Notification(
                title=variant["title"],
                body=campaign.template.body_template,  # Use template body
                variant_id=variant["variant_id"],
                ab_test_group=test.campaign_id,
                campaign_id=campaign.id
            )
            db.add(notification)
        
        db.commit()
        
        return {
            "status": "created",
            "campaign_id": test.campaign_id,
            "variants": test.variants,
            "test_duration": test.test_duration
        }
    except Exception as e:
        logger.error(f"Failed to create A/B test: {str(e)}")
        db.rollback()
        raise
