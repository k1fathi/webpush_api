from sqlalchemy.orm import Session
from sqlalchemy import func
from db.models import Analytics, WebPush, Campaign
from typing import List, Dict
from datetime import datetime

class AnalyticsRepository:
    def __init__(self, db: Session):
        self.db = db

    async def get_campaign_metrics(
        self,
        campaign_id: int,
        start_date: datetime,
        end_date: datetime
    ) -> Dict:
        """Get campaign performance metrics"""
        metrics = (
            self.db.query(
                func.avg(Analytics.open_rate).label('avg_open_rate'),
                func.avg(Analytics.click_rate).label('avg_click_rate'),
                func.count(Analytics.analytics_id).label('total_sent')
            )
            .join(WebPush)
            .join(Campaign)
            .filter(
                Campaign.campaign_id == campaign_id,
                Analytics.created_at.between(start_date, end_date)
            )
            .first()
        )
        
        return {
            'open_rate': float(metrics.avg_open_rate or 0),
            'click_rate': float(metrics.avg_click_rate or 0),
            'total_sent': metrics.total_sent
        }
