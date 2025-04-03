from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.orm import Session

from db.session import get_session
from models.domain.cdp_integration import CdpIntegrationModel
from repositories.base import BaseRepository


class CdpIntegrationRepository(BaseRepository):
    """Repository for CDP integration operations"""
    
    async def get_by_user_id(self, user_id: str) -> Optional[CdpIntegrationModel]:
        """Get CDP integration by user ID"""
        async with get_session() as session:
            query = select(CdpIntegrationModel).where(CdpIntegrationModel.user_id == user_id)
            result = await session.execute(query)
            return result.scalars().first()
    
    async def get_recent_syncs(self, limit: int = 20) -> List[CdpIntegrationModel]:
        """Get most recent CDP syncs"""
        async with get_session() as session:
            query = select(CdpIntegrationModel).order_by(
                CdpIntegrationModel.last_synced.desc()
            ).limit(limit)
            result = await session.execute(query)
            return list(result.scalars().all())
