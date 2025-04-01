import uuid
from datetime import datetime
from typing import List, Optional, Dict

from sqlalchemy import select, func, and_, or_, desc
from sqlalchemy.ext.asyncio import AsyncSession

from db.session import get_session
from models.domain.campaign import CampaignModel, CampaignStatus, CampaignType
from models.campaign import Campaign
from repositories.base import BaseRepository

class CampaignRepository(BaseRepository):
    """Repository for campaign operations"""
    
    async def create(self, campaign: Campaign) -> Campaign:
        """Create a new campaign"""
        async with get_session() as session:
            db_campaign = CampaignModel(
                id=str(uuid.uuid4()) if not campaign.id else campaign.id,
                name=campaign.name,
                description=campaign.description,
                scheduled_time=campaign.scheduled_time,
                status=campaign.status,
                created_at=campaign.created_at or datetime.now(),
                updated_at=campaign.updated_at or datetime.now(),
                is_recurring=campaign.is_recurring,
                recurrence_pattern=campaign.recurrence_pattern,
                campaign_type=campaign.campaign_type,
                segment_id=getattr(campaign, "segment_id", None),
                template_id=getattr(campaign, "template_id", None)
            )
            session.add(db_campaign)
            await session.commit()
            await session.refresh(db_campaign)
            return Campaign.from_orm(db_campaign)
    
    async def get(self, campaign_id: str) -> Optional[Campaign]:
        """Get a campaign by ID"""
        async with get_session() as session:
            result = await session.execute(
                select(CampaignModel).where(CampaignModel.id == campaign_id)
            )
            db_campaign = result.scalars().first()
            return Campaign.from_orm(db_campaign) if db_campaign else None
    
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[Campaign]:
        """Get all campaigns with pagination"""
        async with get_session() as session:
            result = await session.execute(
                select(CampaignModel)
                .order_by(desc(CampaignModel.created_at))
                .offset(skip).limit(limit)
            )
            db_campaigns = result.scalars().all()
            return [Campaign.from_orm(db_campaign) for db_campaign in db_campaigns]
    
    async def update(self, campaign_id: str, campaign: Campaign) -> Campaign:
        """Update a campaign"""
        async with get_session() as session:
            result = await session.execute(
                select(CampaignModel).where(CampaignModel.id == campaign_id)
            )
            db_campaign = result.scalars().first()
            if not db_campaign:
                raise ValueError(f"Campaign with ID {campaign_id} not found")
                
            # Update attributes
            db_campaign.name = campaign.name
            db_campaign.description = campaign.description
            db_campaign.scheduled_time = campaign.scheduled_time
            db_campaign.status = campaign.status
            db_campaign.updated_at = datetime.now()
            db_campaign.is_recurring = campaign.is_recurring
            db_campaign.recurrence_pattern = campaign.recurrence_pattern
            db_campaign.campaign_type = campaign.campaign_type
            
            # Update optional fields if they exist
            if hasattr(campaign, "segment_id"):
                db_campaign.segment_id = campaign.segment_id
                
            if hasattr(campaign, "template_id"):
                db_campaign.template_id = campaign.template_id
            
            await session.commit()
            await session.refresh(db_campaign)
            return Campaign.from_orm(db_campaign)
    
    async def delete(self, campaign_id: str) -> bool:
        """Delete a campaign"""
        async with get_session() as session:
            result = await session.execute(
                select(CampaignModel).where(CampaignModel.id == campaign_id)
            )
            db_campaign = result.scalars().first()
            if db_campaign:
                await session.delete(db_campaign)
                await session.commit()
                return True
            return False
    
    async def get_by_status(self, status: CampaignStatus) -> List[Campaign]:
        """Get campaigns by status"""
        async with get_session() as session:
            result = await session.execute(
                select(CampaignModel).where(CampaignModel.status == status)
            )
            db_campaigns = result.scalars().all()
            return [Campaign.from_orm(db_campaign) for db_campaign in db_campaigns]
    
    async def get_ready_campaigns(self) -> List[Campaign]:
        """Get campaigns that are scheduled and ready to be sent"""
        now = datetime.now()
        async with get_session() as session:
            result = await session.execute(
                select(CampaignModel).where(
                    and_(
                        CampaignModel.status == CampaignStatus.SCHEDULED,
                        CampaignModel.scheduled_time <= now
                    )
                )
            )
            db_campaigns = result.scalars().all()
            return [Campaign.from_orm(db_campaign) for db_campaign in db_campaigns]
    
    async def get_by_type(self, campaign_type: CampaignType) -> List[Campaign]:
        """Get campaigns by type"""
        async with get_session() as session:
            result = await session.execute(
                select(CampaignModel).where(CampaignModel.campaign_type == campaign_type)
            )
            db_campaigns = result.scalars().all()
            return [Campaign.from_orm(db_campaign) for db_campaign in db_campaigns]
    
    async def get_by_segment(self, segment_id: str) -> List[Campaign]:
        """Get campaigns targeting a specific segment"""
        async with get_session() as session:
            result = await session.execute(
                select(CampaignModel).where(CampaignModel.segment_id == segment_id)
            )
            db_campaigns = result.scalars().all()
            return [Campaign.from_orm(db_campaign) for db_campaign in db_campaigns]
    
    async def get_by_template(self, template_id: str) -> List[Campaign]:
        """Get campaigns using a specific template"""
        async with get_session() as session:
            result = await session.execute(
                select(CampaignModel).where(CampaignModel.template_id == template_id)
            )
            db_campaigns = result.scalars().all()
            return [Campaign.from_orm(db_campaign) for db_campaign in db_campaigns]
    
    async def count_campaigns(self) -> int:
        """Count total campaigns"""
        async with get_session() as session:
            result = await session.execute(select(func.count(CampaignModel.id)))
            return result.scalar() or 0
    
    async def count_by_status(self, status: CampaignStatus) -> int:
        """Count campaigns by status"""
        async with get_session() as session:
            result = await session.execute(
                select(func.count(CampaignModel.id))
                .where(CampaignModel.status == status)
            )
            return result.scalar() or 0
