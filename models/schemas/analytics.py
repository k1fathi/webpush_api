import uuid
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, Field

class ConversionType(str, Enum):
    PURCHASE = "purchase"
    SIGNUP = "signup"
    PAGEVIEW = "pageview"
    DOWNLOAD = "download"
    CUSTOM = "custom"

class Analytics(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    notification_id: str
    campaign_id: str
    user_id: str
    delivered: bool = False
    opened: bool = False
    clicked: bool = False
    event_time: datetime = Field(default_factory=datetime.now)
    user_action: Optional[str] = None
    conversion_type: Optional[ConversionType] = None
    conversion_value: float = 0.0
    
    model_config = {"from_attributes": True}

class AnalyticsBase(BaseModel):
    """Base schema for analytics"""
    notification_id: str
    campaign_id: str
    user_id: str
    delivered: bool = False
    opened: bool = False
    clicked: bool = False
    user_action: Optional[str] = None
    
    model_config = {
        "from_attributes": True
    }

class AnalyticsCreate(AnalyticsBase):
    """Schema for creating analytics"""
    event_time: datetime = Field(default_factory=datetime.now)
    conversion_type: Optional[ConversionType] = None
    conversion_value: float = 0.0

class AnalyticsUpdate(BaseModel):
    """Schema for updating analytics"""
    delivered: Optional[bool] = None
    opened: Optional[bool] = None
    clicked: Optional[bool] = None
    event_time: Optional[datetime] = None
    user_action: Optional[str] = None
    conversion_type: Optional[ConversionType] = None
    conversion_value: Optional[float] = None

class AnalyticsRead(AnalyticsBase):
    """Schema for reading analytics"""
    id: str
    event_time: datetime
    conversion_type: Optional[ConversionType] = None
    conversion_value: float = 0.0
    
    model_config = {
        "from_attributes": True
    }

class ConversionCreate(BaseModel):
    """Schema for creating conversion events"""
    notification_id: str
    conversion_type: ConversionType
    value: float = 0.0

class CampaignStats(BaseModel):
    """Schema for campaign statistics"""
    campaign_id: str
    total_notifications: int
    delivered: int
    opened: int
    clicked: int
    conversions: int
    delivery_rate: float
    open_rate: float
    click_rate: float
    conversion_rate: float
    conversion_types: Dict[str, Dict[str, float]]
    avg_time_to_open: float
    calculated_at: datetime

class TimeSeriesDataPoint(BaseModel):
    """Schema for time series data point"""
    date: str
    sends: int
    deliveries: int
    opens: int
    clicks: int
    conversions: int

class CampaignTimeSeriesStats(BaseModel):
    """Schema for campaign time series statistics"""
    campaign_id: str
    start_date: str
    end_date: str
    daily_data: List[TimeSeriesDataPoint]
