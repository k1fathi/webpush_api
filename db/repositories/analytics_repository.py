from sqlalchemy.orm import Session
from sqlalchemy import func, case
from db.models import Analytics, WebPush, Campaign, NotificationAction
from typing import List, Dict
from datetime import datetime, timedelta

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

    async def track_delivery(self, webpush_id: int, status: str) -> Analytics:
        analytics = Analytics(
            webpush_id=webpush_id,
            delivery_status=status,
            created_at=datetime.utcnow()
        )
        self.db.add(analytics)
        self.db.commit()
        self.db.refresh(analytics)
        return analytics

    async def get_campaign_performance(self, campaign_id: int) -> Dict:
        now = datetime.utcnow()
        yesterday = now - timedelta(days=1)
        
        actions = (
            self.db.query(
                NotificationAction.action_type,
                func.count(NotificationAction.id).label('count')
            )
            .join(WebPush)
            .filter(
                WebPush.campaign_id == campaign_id,
                NotificationAction.timestamp >= yesterday
            )
            .group_by(NotificationAction.action_type)
            .all()
        )
        
        return {
            action_type: count
            for action_type, count in actions
        }

    async def get_real_time_stats(self, campaign_id: int) -> Dict:
        stats = (
            self.db.query(
                func.count(Analytics.analytics_id).label('total'),
                func.sum(case(
                    (Analytics.delivery_status == 'delivered', 1),
                    else_=0
                )).label('delivered'),
                func.sum(case(
                    (Analytics.delivery_status == 'failed', 1),
                    else_=0
                )).label('failed')
            )
            .join(WebPush)
            .filter(WebPush.campaign_id == campaign_id)
            .first()
        )
        
        return {
            'total': stats.total,
            'delivered': stats.delivered,
            'failed': stats.failed
        }
