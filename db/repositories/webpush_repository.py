from sqlalchemy.orm import Session
from db.models import Notification, NotificationAction, NotificationSchedule
from typing import List, Optional
from datetime import datetime

class WebPushRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, notification: dict) -> Notification:
        db_notification = Notification(**notification)
        self.db.add(db_notification)
        self.db.commit()
        self.db.refresh(db_notification)
        return db_notification

    def get_by_id(self, notification_id: int) -> Optional[Notification]:
        return self.db.query(Notification).filter(Notification.id == notification_id).first()

    def list(self, skip: int = 0, limit: int = 100) -> List[Notification]:
        return self.db.query(Notification).offset(skip).limit(limit).all()

    async def get_pending_notifications(self) -> List[Notification]:
        return self.db.query(Notification).filter(
            Notification.status == "pending",
            Notification.scheduled_time <= datetime.utcnow()
        ).all()

    async def track_notification_action(self, notification_id: int, action_type: str) -> NotificationAction:
        action = NotificationAction(
            notification_id=notification_id,
            action_type=action_type,
            timestamp=datetime.utcnow()
        )
        self.db.add(action)
        self.db.commit()
        self.db.refresh(action)
        return action

    async def update_notification_status(self, notification_id: int, status: str) -> Optional[Notification]:
        notification = self.get_by_id(notification_id)
        if notification:
            notification.status = status
            notification.updated_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(notification)
        return notification

    async def schedule_notification(self, notification_id: int, schedule_time: datetime) -> NotificationSchedule:
        schedule = NotificationSchedule(
            notification_id=notification_id,
            schedule_time=schedule_time
        )
        self.db.add(schedule)
        self.db.commit()
        self.db.refresh(schedule)
        return schedule
