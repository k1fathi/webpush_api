from fastapi import FastAPI, Depends, HTTPException, Query
import logging
from sqlalchemy.orm import Session
from core.database import get_db
from core.models import (
    Notification, Subscription, NotificationAction, 
    NotificationSchedule, NotificationTracking, NotificationSegment,
    Template, Campaign, WebhookEvent, CampaignSegment  # Add CampaignSegment here
)
from workers.tasks import process_notification, process_webhook_event
from typing import List, Dict, Any
from datetime import datetime
from pydantic import BaseModel
from api.schemas import (
    NotificationCreate, NotificationResponse,
    ActionCreate, ScheduleCreate, TrackingCreate, SegmentCreate,
    TriggerCreate, ABTestCreate, WebhookCreate,
    CDPProfileSync, DashboardMetrics, SegmentPerformance,
    TemplateCreate, TemplateResponse,
    CampaignCreate, CampaignResponse,
    AnalyticsResponse, CampaignAnalytics  # Add these imports
)
from api.services import analytics, segment_service, cdp_service

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="WebPush API")

@app.on_event("startup")
async def startup_event():
    logger.info("Starting up FastAPI application")
    try:
        from core.database import init_db
        logger.info("Initializing database...")
        init_db()
        logger.info("✅ Application startup complete")
    except Exception as e:
        logger.error(f"❌ Startup failed: {str(e)}")
        raise

class NotificationCreate(BaseModel):
    title: str
    body: str
    icon: str = None
    data: dict = None

class NotificationResponse(BaseModel):
    id: int
    title: str
    body: str
    icon: str = None
    data: dict = None
    created_at: datetime

    class Config:
        orm_mode = True

@app.post("/notifications/", response_model=NotificationResponse)
async def create_notification(notification: NotificationCreate, db: Session = Depends(get_db)):
    db_notification = Notification(
        title=notification.title,
        body=notification.body,
        icon=str(notification.icon) if notification.icon else None,
        image=str(notification.image) if notification.image else None,
        badge=notification.badge,
        data=notification.data,
        priority=notification.priority,
        ttl=notification.ttl,
        require_interaction=notification.require_interaction,
        variant_id=notification.variant_id,
        ab_test_group=notification.ab_test_group
    )
    
    if notification.schedule:
        db_notification.schedule = NotificationSchedule(**notification.schedule.dict())
    
    if notification.tracking:
        db_notification.tracking = NotificationTracking(**notification.tracking.dict())
    
    if notification.actions:
        db_notification.actions = [
            NotificationAction(**action.dict())
            for action in notification.actions
        ]
    
    if notification.segments:
        db_notification.segments = [
            NotificationSegment(**segment.dict())
            for segment in notification.segments
        ]

    db.add(db_notification)
    db.commit()
    db.refresh(db_notification)
    
    # Queue notification for processing
    process_notification.delay(db_notification.id)
    
    return db_notification

@app.get("/notifications/", response_model=List[NotificationResponse])
def get_notifications(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    notifications = db.query(Notification).offset(skip).limit(limit).all()
    return notifications

@app.get("/notifications/{notification_id}", response_model=NotificationResponse)
def get_notification(notification_id: int, db: Session = Depends(get_db)):
    notification = db.query(Notification).filter(Notification.id == notification_id).first()
    if notification is None:
        raise HTTPException(status_code=404, detail="Notification not found")
    return notification

@app.get("/health")
async def health_check():
    try:
        # Add more comprehensive health checks
        from core.database import engine
        # Test DB
        engine.connect()
        # Test Redis if needed
        # Test RabbitMQ if needed
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "version": "1.0.0"
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(
            status_code=500,
            detail={"status": "unhealthy", "error": str(e)}
        )

# Update template endpoints
@app.post("/api/templates", response_model=TemplateResponse)  # Note: removed trailing slash
async def create_template(template: TemplateCreate, db: Session = Depends(get_db)):
    db_template = Template(**template.dict())
    db.add(db_template)
    db.commit()
    db.refresh(db_template)
    return db_template

# Template endpoints
@app.get("/api/templates", response_model=List[TemplateResponse])
async def get_templates(
    skip: int = 0, 
    limit: int = 100, 
    category: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get all templates with optional category filter"""
    query = db.query(Template)
    if category:
        query = query.filter(Template.category == category)
    templates = query.offset(skip).limit(limit).all()
    return templates

@app.get("/api/templates/{template_id}", response_model=TemplateResponse)
async def get_template(template_id: int, db: Session = Depends(get_db)):
    """Get template by ID"""
    template = db.query(Template).filter(Template.id == template_id).first()
    if not template:
        raise HTTPException(
            status_code=404,
            detail=f"Template with id {template_id} not found"
        )
    return template

@app.get("/api/campaigns/{campaign_id}/template", response_model=TemplateResponse)
async def get_campaign_template(campaign_id: int, db: Session = Depends(get_db)):
    """Get template associated with a campaign"""
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not campaign:
        raise HTTPException(
            status_code=404,
            detail=f"Campaign with id {campaign_id} not found"
        )
    
    template = db.query(Template).filter(Template.id == campaign.template_id).first()
    if not template:
        raise HTTPException(
            status_code=404,
            detail=f"Template not found for campaign {campaign_id}"
        )
    return template

# Update campaign endpoints
@app.post("/api/campaigns", response_model=CampaignResponse)
async def create_campaign(campaign: CampaignCreate, db: Session = Depends(get_db)):
    """Create a new campaign with segments"""
    # First check if template exists
    template = db.query(Template).filter(Template.id == campaign.template_id).first()
    if not template:
        raise HTTPException(
            status_code=404,
            detail=f"Template with id {campaign.template_id} not found. Please create template first."
        )

    campaign_data = campaign.dict(exclude={'segments'})
    db_campaign = Campaign(**campaign_data)

    # Add segments
    if campaign.segments:
        db_campaign.campaign_segments = [
            CampaignSegment(segment_name=segment_name)
            for segment_name in campaign.segments
        ]
    
    try:
        db.add(db_campaign)
        db.commit()
        db.refresh(db_campaign)
        return db_campaign
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to create campaign: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to create campaign. Please ensure all required data is valid."
        )

# Update analytics endpoints
@app.get("/api/analytics/campaign/{campaign_id}", response_model=AnalyticsResponse)
async def get_campaign_analytics(
    campaign_id: int,
    start_date: datetime = Query(None),
    end_date: datetime = Query(None),
    db: Session = Depends(get_db)
):
    """Get campaign analytics with segment performance and A/B test results"""
    campaign_metrics = await analytics.get_campaign_metrics(
        campaign_id=campaign_id,
        start_date=start_date,
        end_date=end_date,
        db=db
    )
    return campaign_metrics

@app.post("/webhooks/{event_type}")
async def process_webhook(event_type: str, payload: Dict[str, Any], db: Session = Depends(get_db)):
    event = WebhookEvent(
        event_type=event_type,
        payload=payload,
        notification_id=payload.get("notification_id"),
        subscription_id=payload.get("subscription_id")
    )
    db.add(event)
    db.commit()
    process_webhook_event.delay(event.id)
    return {"status": "accepted"}

# Segment Management
@app.post("/api/segments", response_model=Dict[str, Any])
async def create_segment(segment: SegmentCreate, db: Session = Depends(get_db)):
    return await segment_service.create_segment(segment, db)

@app.get("/api/segments", response_model=List[Dict[str, Any]])
async def list_segments(db: Session = Depends(get_db)):
    return await segment_service.list_segments(db)

# Campaign Analytics
@app.get("/api/analytics/campaigns/{campaign_id}")
async def get_campaign_analytics(
    campaign_id: str,
    metrics: List[str] = Query(["delivery_rate", "ctr", "conversion_rate"]),
    db: Session = Depends(get_db)
):
    return await analytics.get_campaign_metrics(campaign_id, metrics, db)

# A/B Testing
@app.post("/api/ab-tests", response_model=Dict[str, Any])  # Added response model
async def create_ab_test(test: ABTestCreate, db: Session = Depends(get_db)):
    """Create a new A/B test for a campaign"""
    return await analytics.create_ab_test(test, db)

# Webhooks
@app.post("/api/webhooks")
async def register_webhook(webhook: WebhookCreate, db: Session = Depends(get_db)):
    return await segment_service.register_webhook(webhook, db)

# CDP Integration
@app.post("/api/cdp/sync")
async def sync_cdp_profile(profile: CDPProfileSync, db: Session = Depends(get_db)):
    return await cdp_service.sync_user_profile(profile, db)

# Dashboard
@app.get("/api/dashboard/segments")
async def get_segment_performance(
    date_range: str = Query("last_7_days"),
    db: Session = Depends(get_db)
):
    return await analytics.get_segment_metrics(date_range, db)

# User Notifications
@app.post("/api/users/{user_id}/notifications")
async def send_user_notification(
    user_id: str,
    notification: NotificationCreate,
    db: Session = Depends(get_db)
):
    return await segment_service.send_targeted_notification(user_id, notification, db)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)



