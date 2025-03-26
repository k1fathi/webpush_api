from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from database import get_db
from models import Notification, Subscription
from celery_worker import celery_app
from sqlalchemy import func

app = FastAPI()

@app.post("/notifications/")
async def create_notification(notification_data: dict, db: Session = Depends(get_db)):
    notification = Notification(
        template=notification_data.get("template"),
        segments=notification_data.get("segments"),
        notification_metadata=notification_data.get("metadata")  # Updated attribute name
    )
    db.add(notification)
    db.commit()
    
    celery_app.send_task(
        'tasks.process_notification', 
        args=[notification.id],
        queue='notifications'
    )
    return {"id": notification.id, "status": "queued"}

@app.get("/notifications/{notification_id}")
async def get_notification(notification_id: int, db: Session = Depends(get_db)):
    return db.query(Notification).filter(Notification.id == notification_id).first()
