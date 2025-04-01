from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import datetime
from typing import List, Optional
from db.models.webpush_model import WebPush

class WebPushRepository:
    def __init__(self, db: Session):
        self.db = db

    async def create(self, webpush_data: dict) -> WebPush:
        db_webpush = WebPush(**webpush_data)
        self.db.add(db_webpush)
        self.db.commit()
        self.db.refresh(db_webpush)
        return db_webpush

    async def get_by_id(self, webpush_id: int) -> Optional[WebPush]:
        return self.db.query(WebPush).filter(WebPush.webpush_id == webpush_id).first()

    async def get_by_campaign(self, campaign_id: int) -> List[WebPush]:
        return self.db.query(WebPush).filter(WebPush.campaign_id == campaign_id).all()

    async def update_status(self, webpush_id: int, status: str) -> Optional[WebPush]:
        webpush = await self.get_by_id(webpush_id)
        if webpush:
            webpush.status = status
            if status == 'delivered':
                webpush.delivered_at = datetime.utcnow()
            elif status == 'clicked':
                webpush.clicked_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(webpush)
        return webpush

    async def get_pending_notifications(self) -> List[WebPush]:
        return self.db.query(WebPush).filter(
            and_(
                WebPush.status == 'pending',
                WebPush.sent_at.is_(None)
            )
        ).all()
