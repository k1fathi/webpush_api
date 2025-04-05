from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import JSONResponse

from api.deps import get_current_active_user
from models.schemas.campaign_template import TemplateCategory, TemplateStatus
from models.schemas.campaign_template import (
    CampaignTemplateCreate, CampaignTemplateRead, 
    CampaignTemplateUpdate, CampaignTemplateList
)
from models.schemas.user import UserRead
from services.campaign_template import CampaignTemplateService

router = APIRouter()

@router.post("/", response_model=CampaignTemplateRead)
async def create_campaign_template(
    template: CampaignTemplateCreate,
    template_service: CampaignTemplateService = Depends(),
    current_user: UserRead = Depends(get_current_active_user)
):
    """Create a new campaign template"""
    return await template_service.create_template(template, UUID(current_user.id))

@router.get("/{template_id}", response_model=CampaignTemplateRead)
async def get_campaign_template(
    template_id: UUID,
    template_service: CampaignTemplateService = Depends(),
    current_user: UserRead = Depends(get_current_active_user)
):
    """Get a campaign template by ID"""
    template = await template_service.get_template(template_id)
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Campaign template with ID {template_id} not found"
        )
    return template

@router.put("/{template_id}", response_model=CampaignTemplateRead)
async def update_campaign_template(
    template_id: UUID,
    template_data: CampaignTemplateUpdate,
    template_service: CampaignTemplateService = Depends(),
    current_user: UserRead = Depends(get_current_active_user)
):
    """Update a campaign template"""
    updated_template = await template_service.update_template(template_id, template_data)
    if not updated_template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Campaign template with ID {template_id} not found"
        )
    return updated_template

@router.get("/", response_model=CampaignTemplateList)
async def list_campaign_templates(
    skip: int = 0,
    limit: int = 100,
    category: Optional[TemplateCategory] = None,
    status: Optional[TemplateStatus] = None,
    template_service: CampaignTemplateService = Depends(),
    current_user: UserRead = Depends(get_current_active_user)
):
    """List campaign templates with optional filtering"""
    filters = {}
    if category:
        filters["category"] = category
    if status:
        filters["status"] = status
    
    return await template_service.list_templates(skip=skip, limit=limit, **filters)

@router.delete("/{template_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_campaign_template(
    template_id: UUID,
    template_service: CampaignTemplateService = Depends(),
    current_user: UserRead = Depends(get_current_active_user)
):
    """Delete a campaign template"""
    deleted = await template_service.delete_template(template_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Campaign template with ID {template_id} not found"
        )
    return JSONResponse(status_code=status.HTTP_204_NO_CONTENT)
