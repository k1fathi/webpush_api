from typing import List, Optional, Dict, Any, Tuple
from uuid import UUID

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from db.session import get_async_session
from models.schemas.campaign_template import (
    CampaignTemplateCreate, CampaignTemplateRead, 
    CampaignTemplateUpdate, CampaignTemplateList
)
from repositories.campaign_template import CampaignTemplateRepository

class CampaignTemplateService:
    def __init__(self, session: AsyncSession = Depends(get_async_session)):
        self.repository = CampaignTemplateRepository(session)
    
    async def create_template(self, data: CampaignTemplateCreate, user_id: UUID) -> CampaignTemplateRead:
        """Create a new template"""
        template = await self.repository.create(data, created_by=user_id)
        return CampaignTemplateRead.model_validate(template)
    
    async def get_template(self, template_id: UUID) -> Optional[CampaignTemplateRead]:
        """Get a template by ID"""
        template = await self.repository.get(template_id)
        if not template:
            return None
        return CampaignTemplateRead.model_validate(template)
    
    async def update_template(self, template_id: UUID, data: CampaignTemplateUpdate) -> Optional[CampaignTemplateRead]:
        """Update a template"""
        template = await self.repository.update(template_id, data)
        if not template:
            return None
        return CampaignTemplateRead.model_validate(template)
    
    async def list_templates(self, skip: int = 0, limit: int = 100, **filters) -> CampaignTemplateList:
        """List templates with optional filtering"""
        items, total = await self.repository.list(skip=skip, limit=limit, **filters)
        return CampaignTemplateList(
            items=[CampaignTemplateRead.model_validate(item) for item in items],
            total=total
        )
    
    async def delete_template(self, template_id: UUID) -> bool:
        """Delete a template"""
        return await self.repository.delete(template_id)
