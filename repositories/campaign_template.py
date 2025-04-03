from typing import List, Optional, Dict, Any
from uuid import UUID

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from models.domain.campaign_template import CampaignTemplateModel
from models.schemas.campaign_template import CampaignTemplateCreate, CampaignTemplateUpdate

class CampaignTemplateRepository:
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create(self, data: CampaignTemplateCreate, created_by: Optional[UUID] = None) -> CampaignTemplateModel:
        """Create a new campaign template"""
        template = CampaignTemplateModel(
            name=data.name,
            description=data.description,
            category=data.category,
            content=data.content,
            created_by=created_by
        )
        
        self.session.add(template)
        await self.session.commit()
        await self.session.refresh(template)
        return template
    
    async def get(self, template_id: UUID) -> Optional[CampaignTemplateModel]:
        """Get template by ID"""
        return await self.session.get(CampaignTemplateModel, template_id)
    
    async def update(self, template_id: UUID, data: CampaignTemplateUpdate) -> Optional[CampaignTemplateModel]:
        """Update a template"""
        template = await self.get(template_id)
        if not template:
            return None
        
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(template, field, value)
        
        await self.session.commit()
        await self.session.refresh(template)
        return template
    
    async def list(self, skip: int = 0, limit: int = 100, **filters) -> tuple[List[CampaignTemplateModel], int]:
        """List templates with optional filtering"""
        query = select(CampaignTemplateModel)
        
        if filters.get("category"):
            query = query.where(CampaignTemplateModel.category == filters["category"])
        if filters.get("status"):
            query = query.where(CampaignTemplateModel.status == filters["status"])
            
        count_query = select(func.count()).select_from(query.subquery())
        total = await self.session.execute(count_query)
        total_count = total.scalar() or 0
        
        query = query.offset(skip).limit(limit).order_by(CampaignTemplateModel.created_at.desc())
        result = await self.session.execute(query)
        items = result.scalars().all()
        
        return list(items), total_count
    
    async def delete(self, template_id: UUID) -> bool:
        """Delete a template"""
        template = await self.get(template_id)
        if not template:
            return False
        
        await self.session.delete(template)
        await self.session.commit()
        return True
