from sqlalchemy.orm import Session
from db.models import Campaign, WebPush, CampaignTemplate, CampaignRecipient
from typing import List, Optional, Dict
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

    async def create_campaign_with_template(self, campaign_data: dict, template_data: dict) -> Campaign:
        campaign = Campaign(**campaign_data)
        template = CampaignTemplate(**template_data, campaign=campaign)
        self.db.add_all([campaign, template])
        self.db.commit()
        self.db.refresh(campaign)
        return campaign

    async def add_recipients(self, campaign_id: int, recipient_ids: List[int]) -> List[CampaignRecipient]:
        recipients = [
            CampaignRecipient(campaign_id=campaign_id, recipient_id=rid)
            for rid in recipient_ids
        ]
        self.db.add_all(recipients)
        self.db.commit()
        return recipients

    async def get_campaign_template(self, campaign_id: int) -> Optional[CampaignTemplate]:
        return self.db.query(CampaignTemplate).filter(
            CampaignTemplate.campaign_id == campaign_id
        ).first()

    async def get_campaign_recipients(self, campaign_id: int) -> List[CampaignRecipient]:
        return self.db.query(CampaignRecipient).filter(
            CampaignRecipient.campaign_id == campaign_id
        ).all()
