from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from db.config import get_db
from datetime import datetime, timedelta
from typing import List, Dict
from api.services.analytics import AnalyticsService

router = APIRouter(prefix="/api/analytics", tags=["analytics"])

@router.get("/campaigns/{campaign_id}/performance")
async def get_campaign_performance(
    campaign_id: int,
    start_date: datetime = None,
    end_date: datetime = None,
    db: Session = Depends(get_db)
):
    """Get detailed campaign performance metrics"""
    analytics_service = AnalyticsService(db)
    return await analytics_service.get_campaign_metrics(campaign_id, start_date, end_date)

@router.get("/segments/performance")
async def get_segment_performance(
    date_range: str = Query("7d"),
    db: Session = Depends(get_db)
):
    """Get performance metrics by segment"""
    analytics_service = AnalyticsService(db)
    return await analytics_service.get_segment_metrics(date_range)
