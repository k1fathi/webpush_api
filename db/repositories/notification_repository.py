from sqlalchemy.orm import Session
from db.models import Notification, NotificationAction, NotificationSchedule
from typing import List, Optional

class NotificationRepository:
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
