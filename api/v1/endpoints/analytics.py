import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from fastapi.responses import JSONResponse

from api.deps import get_current_active_user
from core.exceptions.http import NotFoundException
from core.permissions.dependencies import has_permission
from models.domain.user import UserModel
from models.schemas.analytics import (
    AnalyticsCreate,
    AnalyticsRead,
    AnalyticsUpdate,
    CampaignStats,
    ConversionCreate,
    ConversionType
)
from services.analytics import AnalyticsService
from services.campaign import CampaignService
from utils.audit import audit_log

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get(
    "/campaign/{campaign_id}",
    response_model=CampaignStats,
    dependencies=[Depends(has_permission("read_analytics"))]
)
async def get_campaign_statistics(
    campaign_id: str = Path(...),
    analytics_service: AnalyticsService = Depends(),
):
    """Get statistics for a campaign"""
    try:
        stats = await analytics_service.get_campaign_statistics(campaign_id)
        return stats
    except ValueError as e:
        raise NotFoundException(str(e))
    except Exception as e:
        logger.error(f"Error getting campaign statistics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting campaign statistics: {str(e)}"
        )

@router.post(
    "/track/conversion",
    response_model=AnalyticsRead,
    dependencies=[Depends(has_permission("create_analytics"))]
)
async def track_conversion(
    conversion: ConversionCreate,
    analytics_service: AnalyticsService = Depends(),
):
    """Track a conversion event"""
    try:
        analytics = await analytics_service.record_conversion(
            conversion.notification_id,
            conversion.conversion_type,
            conversion.value
        )
        return analytics
    except ValueError as e:
        raise NotFoundException(str(e))
    except Exception as e:
        logger.error(f"Error recording conversion: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error recording conversion: {str(e)}"
        )

@router.get(
    "/export/campaign/{campaign_id}",
    dependencies=[Depends(has_permission("export_analytics"))]
)
async def export_campaign_analytics(
    campaign_id: str = Path(...),
    format: str = Query("json", enum=["json", "csv"]),
    analytics_service: AnalyticsService = Depends(),
):
    """Export analytics data for a campaign"""
    try:
        stats = await analytics_service.get_campaign_statistics(campaign_id)
        
        if format == "csv":
            # Generate CSV
            csv_content = "Metric,Value\n"
            for key, value in stats.items():
                if isinstance(value, dict):
                    continue  # Skip nested dictionaries
                csv_content += f"{key},{value}\n"
                
            # Return CSV file
            return JSONResponse(
                content={"download_url": f"/api/analytics/download/{campaign_id}?format=csv"},
                status_code=200
            )
        else:
            # Return JSON
            return stats
    except ValueError as e:
        raise NotFoundException(str(e))
    except Exception as e:
        logger.error(f"Error exporting campaign analytics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error exporting campaign analytics: {str(e)}"
        )

@router.get(
    "/time-series/campaign/{campaign_id}",
    dependencies=[Depends(has_permission("read_analytics"))]
)
async def get_campaign_time_series(
    campaign_id: str = Path(...),
    days: int = Query(7, ge=1, le=90),
    analytics_service: AnalyticsService = Depends(),
):
    """Get time series analytics data for a campaign"""
    # This would return time-series data for a campaign
    # Implementation depends on your time series storage
    # This is a placeholder that returns mock data
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    # Create daily data points
    daily_data = []
    current_date = start_date
    
    # Generate mock data for each day
    while current_date <= end_date:
        daily_data.append({
            "date": current_date.strftime("%Y-%m-%d"),
            "sends": 0,  # Would be actual data in real implementation
            "deliveries": 0,
            "opens": 0,
            "clicks": 0,
            "conversions": 0
        })
        current_date += timedelta(days=1)
    
    return {
        "campaign_id": campaign_id,
        "start_date": start_date.strftime("%Y-%m-%d"),
        "end_date": end_date.strftime("%Y-%m-%d"),
        "daily_data": daily_data
    }

@router.get(
    "/summary",
    dependencies=[Depends(has_permission("read_analytics"))]
)
async def get_analytics_summary(
    days: int = Query(30, ge=1, le=365),
    analytics_service: AnalyticsService = Depends(),
):
    """Get a summary of analytics across all campaigns"""
    # This would aggregate data across all campaigns
    # Implementation depends on your specific requirements
    # This is a placeholder
    
    return {
        "period": f"Last {days} days",
        "total_campaigns": 0,
        "total_notifications": 0,
        "total_deliveries": 0,
        "total_opens": 0,
        "total_clicks": 0,
        "total_conversions": 0,
        "average_open_rate": 0,
        "average_click_rate": 0,
        "average_conversion_rate": 0,
        "top_performing_campaign": None
    }
