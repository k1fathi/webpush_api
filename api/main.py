from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from config.settings import settings
import logging
from sqlalchemy.orm import Session
from db.config import get_db
from db.models import (
    Notification, Subscription, NotificationAction, 
    NotificationSchedule, NotificationTracking, NotificationSegment,
    Template, Campaign, WebhookEvent, CampaignSegment,
    User, UserSegment
)
from workers.tasks import process_notification, process_webhook_event
from typing import List, Dict, Any, Optional  # Add Optional here
from datetime import datetime
from pydantic import BaseModel
from api.schemas import (
    NotificationCreate, NotificationResponse,
    ActionCreate, ScheduleCreate, TrackingCreate, SegmentCreate,
    TriggerCreate, ABTestCreate, WebhookCreate,
    CDPProfileSync, DashboardMetrics, SegmentPerformance,
    TemplateCreate, TemplateResponse,
    CampaignCreate, CampaignResponse,
    AnalyticsResponse, CampaignAnalytics
)
from api.services import analytics, segment_service, cdp_service
from api.dependencies import verify_permissions

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="WebPush API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_HOSTS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

    try:
        db = next(get_db())
        setup_default_permissions(db)
        logger.info("✅ Default permissions initialized")
    except Exception as e:
        logger.error(f"❌ Failed to initialize permissions: {str(e)}")
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
async def create_campaign(
    campaign: CampaignCreate,
    db: Session = Depends(get_db),
    _=Depends(verify_permissions([Permission.CAMPAIGN_MANAGEMENT]))
):
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
    db: Session = Depends(get_db),
    _=Depends(verify_permissions([Permission.ANALYTICS_ACCESS]))
):
    return await analytics.get_campaign_metrics(campaign_id, metrics, db)

# A/B Testing
@app.post("/api/ab-tests", response_model=Dict[str, Any])  # Added response model
async def create_ab_test(test: ABTestCreate, db: Session = Depends(get_db)):
    """Create a new A/B test for a campaign"""
    return await analytics.create_ab_test(test, db)

# Webhooks
@app.post("/api/webhooks")
async def register_webhook(
    webhook: WebhookCreate,
    db: Session = Depends(get_db),
    _=Depends(verify_permissions([Permission.SYSTEM_CONFIGURATION]))
):
    return await segment_service.register_webhook(webhook, db)

# Add endpoint to check if user is admin
@app.get("/api/users/me/is-admin")
async def check_admin_status(current_user = Depends(get_current_user)):
    """Check if current user has admin privileges"""
    return {"is_admin": is_admin(current_user)}

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

@app.post("/api/notifications/{notification_id}/cep", response_model=Dict[str, Any])
async def update_cep_strategy(
    notification_id: int,
    strategy: CEPStrategyCreate,
    db: Session = Depends(get_db)
):
    """Update CEP strategy for notification"""
    notification = db.query(Notification).filter(Notification.id == notification_id).first()
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
        
    cep_data = CEPStrategy(
        notification_id=notification_id,
        **strategy.dict()
    )
    db.add(cep_data)
    db.commit()
    return {"status": "success", "strategy": strategy}

@app.post("/api/notifications/{notification_id}/cdp", response_model=Dict[str, Any])
async def update_cdp_data(
    notification_id: int,
    cdp_data: CDPDataCreate,
    db: Session = Depends(get_db)
):
    """Update CDP data for notification"""
    notification = db.query(Notification).filter(Notification.id == notification_id).first()
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
        
    cdp = CDPData(
        notification_id=notification_id,
        **cdp_data.dict()
    )
    db.add(cdp)
    db.commit()
    return {"status": "success", "cdp_data": cdp_data}

@app.put("/api/notifications/{notification_id}/targeting", response_model=Dict[str, Any])
async def update_targeting_rules(
    notification_id: int,
    rules: TargetingRules,
    db: Session = Depends(get_db)
):
    """Update targeting rules for notification"""
    notification = db.query(Notification).filter(Notification.id == notification_id).first()
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
        
    notification.targeting_rules = rules.dict()
    db.commit()
    return {"status": "success", "rules": rules}

# User Management
@app.post("/api/users", response_model=UserResponse)
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """Create a new user"""
    db_user = User(**user.dict())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.get("/api/users/{user_id}/segments", response_model=List[str])
async def get_user_segments(user_id: int, db: Session = Depends(get_db)):
    """Get segments for a user"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return [segment.segment.name for segment in user.segments]

@app.get("/api/users/{user_id}/notifications", response_model=List[NotificationResponse])
async def get_user_notifications(
    user_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get all notifications for a user"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user.notifications[skip:skip + limit]

@app.post("/api/users/{user_id}/roles")
async def assign_user_role(
    user_id: int,
    role_name: str,
    db: Session = Depends(get_db)
):
    """Assign a role to a user with default permissions"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    try:
        assign_default_role_permissions(user, role_name, db)
        return {"status": "success", "message": f"Role {role_name} assigned to user"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/users/{user_id}/permissions")
async def get_user_permissions(user_id: int, db: Session = Depends(get_db)):
    """Get all permissions for a user based on their roles"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    all_permissions = set()
    for role in user.roles:
        all_permissions.update(perm.name for perm in role.permissions)
    
    return {"user_id": user_id, "permissions": list(all_permissions)}

@app.get("/api/roles/{role_name}/activities")
async def get_role_activities(role_name: str, db: Session = Depends(get_db)):
    """Get all activities allowed for a specific role"""
    from db.seeders.role_permission_seeder import SWIMLANE_ACTIVITY_PERMISSIONS
    
    if role_name not in SWIMLANE_ACTIVITY_PERMISSIONS:
        raise HTTPException(status_code=404, detail="Role not found")
    
    return {
        "role": role_name,
        "activities": SWIMLANE_ACTIVITY_PERMISSIONS[role_name]["activities"],
        "permissions": SWIMLANE_ACTIVITY_PERMISSIONS[role_name]["permissions"]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host=settings.API_HOST,
        port=settings.API_PORT,
        workers=settings.API_WORKERS
    )



