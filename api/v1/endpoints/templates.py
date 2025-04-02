import logging
from typing import Dict, List, Optional, Any

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from fastapi.responses import JSONResponse

from api.deps import get_current_active_user
from core.exceptions.http import NotFoundException
from core.permissions.dependencies import has_permission
from models.domain.user import UserModel
from models.schemas.template import (
    TemplateCreate,
    TemplateRead,
    TemplateUpdate,
    TemplateList,
    TemplatePreview,
    TemplateValidation,
    TemplateVersion,
    TemplateStatus,
    TemplateType
)
from services.template import TemplateService
from utils.audit import audit_log

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post(
    "/",
    response_model=TemplateRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(has_permission("create_template"))]
)
async def create_template(
    template: TemplateCreate,
    current_user: UserModel = Depends(get_current_active_user),
    template_service: TemplateService = Depends(),
):
    """Create a new template"""
    try:
        created = await template_service.create_template(
            template.dict(),
            user_id=str(current_user.id)
        )
        return created
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error creating template: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating template: {str(e)}"
        )

@router.get(
    "/",
    response_model=TemplateList,
    dependencies=[Depends(has_permission("list_templates"))]
)
async def list_templates(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    status: Optional[TemplateStatus] = None,
    type: Optional[TemplateType] = None,
    tag: Optional[str] = None,
    category: Optional[str] = None,
    template_service: TemplateService = Depends(),
):
    """List all templates with pagination and filtering"""
    try:
        templates, total = await template_service.get_all_templates(
            skip=skip,
            limit=limit,
            status=status,
            template_type=type,
            tag=tag,
            category=category
        )
        return {
            "items": templates,
            "total": total,
            "skip": skip,
            "limit": limit
        }
    except Exception as e:
        logger.error(f"Error listing templates: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error listing templates: {str(e)}"
        )

@router.get(
    "/{template_id}",
    response_model=TemplateRead,
    dependencies=[Depends(has_permission("read_template"))]
)
async def get_template(
    template_id: str = Path(...),
    template_service: TemplateService = Depends(),
):
    """Get a template by ID"""
    template = await template_service.get_template(template_id)
    if not template:
        raise NotFoundException("Template not found")
    return template

@router.put(
    "/{template_id}",
    response_model=TemplateRead,
    dependencies=[Depends(has_permission("update_template"))]
)
async def update_template(
    template_id: str,
    template: TemplateUpdate,
    current_user: UserModel = Depends(get_current_active_user),
    template_service: TemplateService = Depends(),
):
    """Update a template"""
    try:
        updated = await template_service.update_template(
            template_id=template_id,
            template_data=template.dict(exclude_unset=True),
            user_id=str(current_user.id)
        )
        return updated
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except NotFoundException:
        raise
    except Exception as e:
        logger.error(f"Error updating template: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating template: {str(e)}"
        )

@router.delete(
    "/{template_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(has_permission("delete_template"))]
)
async def delete_template(
    template_id: str = Path(...),
    current_user: UserModel = Depends(get_current_active_user),
    template_service: TemplateService = Depends(),
):
    """Delete a template"""
    try:
        result = await template_service.delete_template(
            template_id=template_id,
            user_id=str(current_user.id)
        )
        if not result:
            raise NotFoundException("Template not found")
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except NotFoundException:
        raise
    except Exception as e:
        logger.error(f"Error deleting template: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting template: {str(e)}"
        )

@router.post(
    "/validate",
    response_model=TemplateValidation,
    dependencies=[Depends(has_permission("create_template"))]
)
async def validate_template(
    template_data: Dict[str, Any],
    template_service: TemplateService = Depends(),
):
    """Validate a template"""
    try:
        validation = await template_service.validate_template(template_data)
        return validation
    except Exception as e:
        logger.error(f"Error validating template: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error validating template: {str(e)}"
        )

@router.post(
    "/{template_id}/render",
    response_model=TemplatePreview,
    dependencies=[Depends(has_permission("read_template"))]
)
async def render_template(
    template_id: str = Path(...),
    data: Dict[str, Any] = None,
    template_service: TemplateService = Depends(),
):
    """Render a template with provided data"""
    try:
        rendered = await template_service.render_template(
            template_id=template_id,
            data=data or {}
        )
        return rendered
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error rendering template: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error rendering template: {str(e)}"
        )

@router.post(
    "/{template_id}/submit",
    response_model=TemplateRead,
    dependencies=[Depends(has_permission("submit_template"))]
)
async def submit_template_for_approval(
    template_id: str = Path(...),
    current_user: UserModel = Depends(get_current_active_user),
    template_service: TemplateService = Depends(),
):
    """Submit a template for approval"""
    try:
        updated = await template_service.submit_for_approval(
            template_id=template_id,
            user_id=str(current_user.id)
        )
        return updated
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except NotFoundException:
        raise
    except Exception as e:
        logger.error(f"Error submitting template: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error submitting template: {str(e)}"
        )

@router.post(
    "/{template_id}/approve",
    response_model=TemplateRead,
    dependencies=[Depends(has_permission("approve_template"))]
)
async def approve_template(
    template_id: str = Path(...),
    current_user: UserModel = Depends(get_current_active_user),
    template_service: TemplateService = Depends(),
):
    """Approve a template"""
    try:
        updated = await template_service.approve_template(
            template_id=template_id,
            user_id=str(current_user.id)
        )
        return updated
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except NotFoundException:
        raise
    except Exception as e:
        logger.error(f"Error approving template: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error approving template: {str(e)}"
        )

@router.post(
    "/{template_id}/reject",
    response_model=TemplateRead,
    dependencies=[Depends(has_permission("approve_template"))]
)
async def reject_template(
    template_id: str = Path(...),
    reason: Optional[str] = None,
    current_user: UserModel = Depends(get_current_active_user),
    template_service: TemplateService = Depends(),
):
    """Reject a template"""
    try:
        updated = await template_service.reject_template(
            template_id=template_id,
            reason=reason,
            user_id=str(current_user.id)
        )
        return updated
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except NotFoundException:
        raise
    except Exception as e:
        logger.error(f"Error rejecting template: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error rejecting template: {str(e)}"
        )

@router.post(
    "/{template_id}/archive",
    response_model=TemplateRead,
    dependencies=[Depends(has_permission("archive_template"))]
)
async def archive_template(
    template_id: str = Path(...),
    current_user: UserModel = Depends(get_current_active_user),
    template_service: TemplateService = Depends(),
):
    """Archive a template"""
    try:
        updated = await template_service.archive_template(
            template_id=template_id,
            user_id=str(current_user.id)
        )
        return updated
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except NotFoundException:
        raise
    except Exception as e:
        logger.error(f"Error archiving template: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error archiving template: {str(e)}"
        )

@router.get(
    "/{template_id}/versions",
    response_model=List[TemplateVersion],
    dependencies=[Depends(has_permission("read_template"))]
)
async def get_template_versions(
    template_id: str = Path(...),
    template_service: TemplateService = Depends(),
):
    """Get all versions of a template"""
    try:
        versions = await template_service.get_template_versions(template_id)
        return versions
    except Exception as e:
        logger.error(f"Error getting template versions: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting template versions: {str(e)}"
        )

@router.post(
    "/{template_id}/restore/{version}",
    response_model=TemplateRead,
    dependencies=[Depends(has_permission("update_template"))]
)
async def restore_template_version(
    template_id: str = Path(...),
    version: int = Path(..., gt=0),
    current_user: UserModel = Depends(get_current_active_user),
    template_service: TemplateService = Depends(),
):
    """Restore a template to a specific version"""
    try:
        updated = await template_service.restore_template_version(
            template_id=template_id,
            version=version,
            user_id=str(current_user.id)
        )
        return updated
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error restoring template version: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error restoring template version: {str(e)}"
        )

@router.get(
    "/search",
    response_model=List[TemplateRead],
    dependencies=[Depends(has_permission("list_templates"))]
)
async def search_templates(
    query: str = Query(..., min_length=1),
    limit: int = Query(10, ge=1, le=50),
    template_service: TemplateService = Depends(),
):
    """Search templates by name or content"""
    try:
        templates = await template_service.search_templates(query, limit)
        return templates
    except Exception as e:
        logger.error(f"Error searching templates: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error searching templates: {str(e)}"
        )
