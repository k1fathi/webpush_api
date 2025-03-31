from sqlalchemy.orm import Session
from db.models import Campaign, WebPush
from typing import List, Optional
from datetime import datetime

class CampaignRepository:
    def __init__(self, db: Session):
        self.db = db

    async def create(self, campaign_data: dict) -> Campaign:
        campaign = Campaign(**campaign_data)
        self.db.add(campaign)
        self.db.commit()
        self.db.refresh(campaign)
        return campaign

    async def get_active_campaigns(self) -> List[Campaign]:
        return self.db.query(Campaign).filter(
            Campaign.status == "active",
            Campaign.start_time <= datetime.utcnow(),
            Campaign.end_time >= datetime.utcnow()
        ).all()

    async def update_status(self, campaign_id: int, status: str) -> Optional[Campaign]:
        campaign = self.db.query(Campaign).filter(Campaign.campaign_id == campaign_id).first()
        if campaign:
            campaign.status = status
            self.db.commit()
            self.db.refresh(campaign)
        return campaign
