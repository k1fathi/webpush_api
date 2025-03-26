from fastapi import FastAPI, Depends, HTTPException
import logging
from sqlalchemy.orm import Session
from core.database import get_db
from core.models import Notification, Subscription
from workers.tasks import process_notification
from typing import List
from datetime import datetime
from pydantic import BaseModel

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
def create_notification(notification: NotificationCreate, db: Session = Depends(get_db)):
    db_notification = Notification(
        title=notification.title,
        body=notification.body,
        icon=notification.icon,
        data=notification.data
    )
    db.add(db_notification)
    db.commit()
    db.refresh(db_notification)
    
    # Queue the notification for processing
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)



