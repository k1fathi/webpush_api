from typing import List, Optional, Dict
from db.repositories.webpush_repository import WebPushRepository
from schemas.webpush_schema import WebPushCreate, WebPushUpdate
from datetime import datetime

class WebPushService:
    def __init__(self, repository: WebPushRepository):
        self.repository = repository

    async def create_notification(self, webpush_data: WebPushCreate) -> WebPushModel:
        data = webpush_data.dict()
        data['status'] = 'pending'
        data['sent_at'] = datetime.utcnow()
        return await self.repository.create(data)

    async def get_notification(self, webpush_id: int) -> Optional[WebPushModel]:
        return await self.repository.get_by_id(webpush_id)

    async def update_status(self, webpush_id: int, status: str) -> Optional[WebPushModel]:
        return await self.repository.update_status(webpush_id, status)

    async def get_campaign_notifications(self, campaign_id: int) -> List[WebPushModel]:
        return await self.repository.get_by_campaign(campaign_id)

    async def process_pending_notifications(self) -> List[WebPushModel]:
        notifications = await self.repository.get_pending_notifications()
        for notification in notifications:
            # Add your notification sending logic here
            await self.repository.update_status(notification.webpush_id, 'sent')
        return notifications
