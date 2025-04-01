import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from sqlalchemy import select, func, and_, or_, desc
from sqlalchemy.ext.asyncio import AsyncSession

from db.session import get_session
from models.domain.analytics import AnalyticsModel
from models.analytics import Analytics, ConversionType
from repositories.base import BaseRepository

class AnalyticsRepository(BaseRepository):
    """Repository for analytics operations"""
    
    async def create(self, analytics: Analytics) -> Analytics:
        """Create a new analytics record"""
        async with get_session() as session:
            db_analytics = AnalyticsModel(
                id=str(uuid.uuid4()) if not analytics.id else analytics.id,
                notification_id=analytics.notification_id,
                campaign_id=analytics.campaign_id,
                user_id=analytics.user_id,
                delivered=analytics.delivered,
                opened=analytics.opened,
                clicked=analytics.clicked,
                event_time=analytics.event_time,
                user_action=analytics.user_action,
                conversion_type=analytics.conversion_type,
                conversion_value=analytics.conversion_value
            )
            session.add(db_analytics)
            await session.commit()
            await session.refresh(db_analytics)
            return Analytics.from_orm(db_analytics)
    
    async def get(self, analytics_id: str) -> Optional[Analytics]:
        """Get an analytics record by ID"""
        async with get_session() as session:
            result = await session.execute(
                select(AnalyticsModel).where(AnalyticsModel.id == analytics_id)
            )
            db_analytics = result.scalars().first()
            return Analytics.from_orm(db_analytics) if db_analytics else None
    
    async def update(self, analytics_id: str, analytics: Analytics) -> Analytics:
        """Update an analytics record"""
        async with get_session() as session:
            result = await session.execute(
                select(AnalyticsModel).where(AnalyticsModel.id == analytics_id)
            )
            db_analytics = result.scalars().first()
            if not db_analytics:
                raise ValueError(f"Analytics record with ID {analytics_id} not found")
                
            # Update attributes
            db_analytics.delivered = analytics.delivered
            db_analytics.opened = analytics.opened
            db_analytics.clicked = analytics.clicked
            db_analytics.event_time = analytics.event_time
            db_analytics.user_action = analytics.user_action
            db_analytics.conversion_type = analytics.conversion_type
            db_analytics.conversion_value = analytics.conversion_value
            
            await session.commit()
            await session.refresh(db_analytics)
            return Analytics.from_orm(db_analytics)
    
    async def delete(self, analytics_id: str) -> bool:
        """Delete an analytics record"""
        async with get_session() as session:
            result = await session.execute(
                select(AnalyticsModel).where(AnalyticsModel.id == analytics_id)
            )
            db_analytics = result.scalars().first()
            if db_analytics:
                await session.delete(db_analytics)
                await session.commit()
                return True
            return False
    
    async def get_by_notification(self, notification_id: str) -> Optional[Analytics]:
        """Get analytics record by notification ID"""
        async with get_session() as session:
            result = await session.execute(
                select(AnalyticsModel)
                .where(AnalyticsModel.notification_id == notification_id)
                .order_by(desc(AnalyticsModel.event_time))
            )
            db_analytics = result.scalars().first()
            return Analytics.from_orm(db_analytics) if db_analytics else None
    
    async def get_by_campaign(self, campaign_id: str) -> List[Analytics]:
        """Get all analytics records for a campaign"""
        async with get_session() as session:
            result = await session.execute(
                select(AnalyticsModel).where(AnalyticsModel.campaign_id == campaign_id)
            )
            db_analytics_list = result.scalars().all()
            return [Analytics.from_orm(db_analytics) for db_analytics in db_analytics_list]
    
    async def get_by_user(self, user_id: str) -> List[Analytics]:
        """Get all analytics records for a user"""
        async with get_session() as session:
            result = await session.execute(
                select(AnalyticsModel).where(AnalyticsModel.user_id == user_id)
            )
            db_analytics_list = result.scalars().all()
            return [Analytics.from_orm(db_analytics) for db_analytics in db_analytics_list]
    
    async def count_delivered_by_campaign(self, campaign_id: str) -> int:
        """Count delivered notifications for a campaign"""
        async with get_session() as session:
            result = await session.execute(
                select(func.count(AnalyticsModel.id))
                .where(
                    and_(
                        AnalyticsModel.campaign_id == campaign_id,
                        AnalyticsModel.delivered == True
                    )
                )
            )
            return result.scalar() or 0
    
    async def count_opened_by_campaign(self, campaign_id: str) -> int:
        """Count opened notifications for a campaign"""
        async with get_session() as session:
            result = await session.execute(
                select(func.count(AnalyticsModel.id))
                .where(
                    and_(
                        AnalyticsModel.campaign_id == campaign_id,
                        AnalyticsModel.opened == True
                    )
                )
            )
            return result.scalar() or 0
    
    async def count_clicked_by_campaign(self, campaign_id: str) -> int:
        """Count clicked notifications for a campaign"""
        async with get_session() as session:
            result = await session.execute(
                select(func.count(AnalyticsModel.id))
                .where(
                    and_(
                        AnalyticsModel.campaign_id == campaign_id,
                        AnalyticsModel.clicked == True
                    )
                )
            )
            return result.scalar() or 0
    
    async def get_conversions_for_campaign(self, campaign_id: str) -> List[Analytics]:
        """Get all conversions for a campaign"""
        async with get_session() as session:
            result = await session.execute(
                select(AnalyticsModel)
                .where(
                    and_(
                        AnalyticsModel.campaign_id == campaign_id,
                        AnalyticsModel.conversion_type != None
                    )
                )
            )
            db_analytics_list = result.scalars().all()
            return [Analytics.from_orm(db_analytics) for db_analytics in db_analytics_list]
    
    async def get_conversions_for_variant(self, variant_id: str) -> List[Analytics]:
        """
        Get conversions for a specific test variant.
        This requires a join with notifications to find those belonging to the variant.
        """
        # This would need to be implemented with proper joins in a real scenario
        # For now, returning empty list as placeholder
        return []
    
    async def get_analytics_by_time_period(
        self, 
        start_time: datetime, 
        end_time: datetime
    ) -> List[Analytics]:
        """Get analytics records within a time period"""
        async with get_session() as session:
            result = await session.execute(
                select(AnalyticsModel)
                .where(
                    and_(
                        AnalyticsModel.event_time >= start_time,
                        AnalyticsModel.event_time <= end_time
                    )
                )
            )
            db_analytics_list = result.scalars().all()
            return [Analytics.from_orm(db_analytics) for db_analytics in db_analytics_list]
