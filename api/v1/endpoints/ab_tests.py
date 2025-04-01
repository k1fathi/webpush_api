from typing import Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from pydantic import BaseModel

from api.deps import get_current_active_user
from core.exceptions.http import NotFoundException
from core.permissions.dependencies import has_permission
from models.domain.user import UserModel
from models.schemas.ab_test import AbTestCreate, AbTestRead, AbTestUpdate
from models.schemas.test_variant import TestVariantCreate, TestVariantRead
from services.ab_test import AbTestService
from utils.audit import audit_log

router = APIRouter()

@router.post(
    "/",
    response_model=AbTestRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(has_permission("create_ab_test"))]
)
async def create_ab_test(
    campaign_id: str,
    ab_test: AbTestCreate,
    current_user: UserModel = Depends(get_current_active_user),
    ab_test_service: AbTestService = Depends(),
):
    """Create a new A/B test for a campaign"""
    try:
        created_test = await ab_test_service.create_test(campaign_id, ab_test.dict())
        return created_test
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get(
    "/{ab_test_id}",
    response_model=AbTestRead,
    dependencies=[Depends(has_permission("read_ab_test"))]
)
async def get_ab_test(
    ab_test_id: str = Path(...),
    ab_test_service: AbTestService = Depends(),
):
    """Get an A/B test by ID"""
    ab_test = await ab_test_service.get_test(ab_test_id)
    if not ab_test:
        raise NotFoundException("A/B test not found")
    return ab_test

@router.get(
    "/campaign/{campaign_id}",
    response_model=List[AbTestRead],
    dependencies=[Depends(has_permission("list_ab_tests"))]
)
async def get_campaign_ab_tests(
    campaign_id: str = Path(...),
    ab_test_service: AbTestService = Depends(),
):
    """Get all A/B tests for a campaign"""
    return await ab_test_service.get_tests_by_campaign(campaign_id)

@router.put(
    "/{ab_test_id}",
    response_model=AbTestRead,
    dependencies=[Depends(has_permission("update_ab_test"))]
)
async def update_ab_test(
    ab_test_id: str,
    ab_test: AbTestUpdate,
    current_user: UserModel = Depends(get_current_active_user),
    ab_test_service: AbTestService = Depends(),
):
    """Update an A/B test"""
    try:
        updated_test = await ab_test_service.update_test(ab_test_id, ab_test.dict(exclude_unset=True))
        return updated_test
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post(
    "/{ab_test_id}/variants",
    response_model=TestVariantRead,
    dependencies=[Depends(has_permission("update_ab_test"))]
)
async def add_test_variant(
    ab_test_id: str,
    variant: TestVariantCreate,
    current_user: UserModel = Depends(get_current_active_user),
    ab_test_service: AbTestService = Depends(),
):
    """Add a variant to an A/B test"""
    try:
        created_variant = await ab_test_service.add_variant(ab_test_id, variant.dict())
        return created_variant
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get(
    "/{ab_test_id}/variants",
    response_model=List[TestVariantRead],
    dependencies=[Depends(has_permission("read_ab_test"))]
)
async def get_test_variants(
    ab_test_id: str,
    ab_test_service: AbTestService = Depends(),
):
    """Get all variants for an A/B test"""
    return await ab_test_service.get_variants(ab_test_id)

@router.post(
    "/{ab_test_id}/activate",
    response_model=AbTestRead,
    dependencies=[Depends(has_permission("update_ab_test"))]
)
async def activate_ab_test(
    ab_test_id: str,
    current_user: UserModel = Depends(get_current_active_user),
    ab_test_service: AbTestService = Depends(),
):
    """Activate an A/B test"""
    try:
        activated_test = await ab_test_service.activate_test(ab_test_id)
        return activated_test
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post(
    "/{ab_test_id}/complete",
    response_model=AbTestRead,
    dependencies=[Depends(has_permission("update_ab_test"))]
)
async def complete_ab_test(
    ab_test_id: str,
    current_user: UserModel = Depends(get_current_active_user),
    ab_test_service: AbTestService = Depends(),
):
    """Mark an A/B test as complete"""
    try:
        completed_test = await ab_test_service.complete_test(ab_test_id)
        return completed_test
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get(
    "/{ab_test_id}/results",
    dependencies=[Depends(has_permission("read_ab_test"))]
)
async def analyze_results(
    ab_test_id: str,
    ab_test_service: AbTestService = Depends(),
):
    """Analyze the results of an A/B test"""
    try:
        results = await ab_test_service.analyze_results(ab_test_id)
        return results
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post(
    "/{ab_test_id}/apply-winner",
    dependencies=[Depends(has_permission("update_ab_test"))]
)
async def apply_winning_variant(
    ab_test_id: str,
    current_user: UserModel = Depends(get_current_active_user),
    ab_test_service: AbTestService = Depends(),
):
    """Apply the winning variant to the campaign"""
    try:
        success = await ab_test_service.apply_winning_variant(ab_test_id)
        if success:
            return {"status": "success", "message": "Winning variant applied successfully"}
        else:
            return {
                "status": "warning", 
                "message": "No significant winner found or could not apply winner"
            }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
