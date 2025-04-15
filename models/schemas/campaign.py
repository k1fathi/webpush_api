"""Schemas for campaign data"""
import enum
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
from uuid import UUID

from pydantic import BaseModel, Field


class CampaignStatus(str, enum.Enum):
    """Campaign status enum"""
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    RUNNING = "running"
    COMPLETED = "completed"
    PAUSED = "paused"
    CANCELLED = "cancelled"


class CampaignType(str, enum.Enum):
    """Campaign type enum"""
    ONE_TIME = "one_time"
    RECURRING = "recurring"
    TRIGGERED = "triggered"


class Campaign(BaseModel):
    """Schema for campaign data"""
    id: Optional[str] = None
    name: str
    description: Optional[str] = None
    scheduled_time: Optional[datetime] = None
    status: CampaignStatus = CampaignStatus.DRAFT
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    is_recurring: bool = False
    recurrence_pattern: Optional[str] = None
    campaign_type: CampaignType = CampaignType.ONE_TIME
    
    # Web Push specific settings
    delivery_policy: Optional[Dict[str, Any]] = None
    throttling_rate: Optional[int] = None
    audience_limit: Optional[int] = None
    
    # Web Push campaign metrics
    sent_count: int = 0
    delivered_count: int = 0
    clicked_count: int = 0
    dismissed_count: int = 0
    failed_count: int = 0
    
    # Performance metrics
    click_rate: Optional[float] = None
    dismiss_rate: Optional[float] = None
    conversion_rate: Optional[float] = None
    
    # A/B testing configuration
    is_ab_test: bool = False
    ab_test_config: Optional[Dict[str, Any]] = None
    
    # Custom notification payload overrides
    custom_notification_options: Optional[Dict[str, Any]] = None
    
    # Foreign keys
    segment_id: Optional[str] = None
    template_id: Optional[str] = None
    web_push_config_id: Optional[str] = None
    created_by: Optional[str] = None
    
    model_config = {"from_attributes": True}


class CampaignCreate(BaseModel):
    """Schema for creating a campaign"""
    name: str = Field(..., description="Campaign name")
    description: Optional[str] = Field(None, description="Campaign description")
    scheduled_time: Optional[datetime] = Field(None, description="Scheduled time")
    status: CampaignStatus = Field(CampaignStatus.DRAFT, description="Campaign status")
    is_recurring: bool = Field(False, description="Is the campaign recurring")
    recurrence_pattern: Optional[str] = Field(None, description="Recurrence pattern")
    campaign_type: CampaignType = Field(CampaignType.ONE_TIME, description="Campaign type")
    
    # Web Push specific settings
    delivery_policy: Optional[Dict[str, Any]] = Field(None, description="Rules for when to deliver notifications")
    throttling_rate: Optional[int] = Field(None, description="Notifications per minute")
    audience_limit: Optional[int] = Field(None, description="Max number of users to target")
    
    # A/B testing configuration
    is_ab_test: bool = Field(False, description="Whether this is an A/B test campaign")
    ab_test_config: Optional[Dict[str, Any]] = Field(None, description="A/B test configuration")
    
    # Custom notification payload overrides
    custom_notification_options: Optional[Dict[str, Any]] = Field(None, description="Custom notification options")
    
    # Foreign keys
    segment_id: Optional[UUID] = Field(None, description="Segment ID")
    template_id: Optional[UUID] = Field(None, description="Template ID")
    web_push_config_id: Optional[UUID] = Field(None, description="Web Push Config ID")
    created_by: Optional[UUID] = Field(None, description="User ID of creator")


class CampaignUpdate(BaseModel):
    """Schema for updating a campaign"""
    name: Optional[str] = Field(None, description="Campaign name")
    description: Optional[str] = Field(None, description="Campaign description")
    scheduled_time: Optional[datetime] = Field(None, description="Scheduled time")
    status: Optional[CampaignStatus] = Field(None, description="Campaign status")
    is_recurring: Optional[bool] = Field(None, description="Is the campaign recurring")
    recurrence_pattern: Optional[str] = Field(None, description="Recurrence pattern")
    campaign_type: Optional[CampaignType] = Field(None, description="Campaign type")
    
    # Web Push specific settings updates
    delivery_policy: Optional[Dict[str, Any]] = Field(None, description="Rules for when to deliver notifications")
    throttling_rate: Optional[int] = Field(None, description="Notifications per minute")
    audience_limit: Optional[int] = Field(None, description="Max number of users to target")
    
    # A/B testing configuration updates
    is_ab_test: Optional[bool] = Field(None, description="Whether this is an A/B test campaign")
    ab_test_config: Optional[Dict[str, Any]] = Field(None, description="A/B test configuration")
    
    # Custom notification payload overrides updates
    custom_notification_options: Optional[Dict[str, Any]] = Field(None, description="Custom notification options")
    
    # Foreign keys updates
    segment_id: Optional[UUID] = Field(None, description="Segment ID")
    template_id: Optional[UUID] = Field(None, description="Template ID")
    web_push_config_id: Optional[UUID] = Field(None, description="Web Push Config ID")


class CampaignRead(BaseModel):
    """Schema for reading a campaign"""
    id: UUID
    name: str
    description: Optional[str]
    scheduled_time: Optional[datetime]
    status: CampaignStatus
    is_recurring: bool
    recurrence_pattern: Optional[str]
    campaign_type: CampaignType
    created_at: datetime
    updated_at: Optional[datetime]
    completed_at: Optional[datetime]
    
    # Web Push specific settings
    delivery_policy: Optional[Dict[str, Any]] = None
    throttling_rate: Optional[int] = None
    audience_limit: Optional[int] = None
    
    # Web Push campaign metrics
    sent_count: int = 0
    delivered_count: int = 0
    clicked_count: int = 0
    dismissed_count: int = 0
    failed_count: int = 0
    
    # Performance metrics
    click_rate: Optional[float] = None
    dismiss_rate: Optional[float] = None
    conversion_rate: Optional[float] = None
    
    # A/B testing configuration
    is_ab_test: bool = False
    ab_test_config: Optional[Dict[str, Any]] = None
    
    # Foreign keys
    segment_id: Optional[UUID]
    template_id: Optional[UUID]
    web_push_config_id: Optional[UUID] = None
    created_by: Optional[UUID] = None


class CampaignList(BaseModel):
    """Schema for listing campaigns with pagination"""
    items: List[CampaignRead]
    total: int
    page: int = 0
    page_size: int = 100


class CampaignPreview(BaseModel):
    """Schema for campaign preview"""
    id: Optional[UUID] = None
    name: str
    description: Optional[str] = None
    template: Dict[str, Any] = Field(default_factory=dict)
    segment_info: Optional[Dict[str, Any]] = None
    scheduled_time: Optional[datetime] = None
    status: CampaignStatus = CampaignStatus.DRAFT
    estimated_audience: Optional[int] = None
    personalization_example: Optional[Dict[str, Any]] = None
    
    # Web Push specific preview
    web_push_config: Optional[Dict[str, Any]] = None
    delivery_policy: Optional[Dict[str, Any]] = None
    throttling_rate: Optional[int] = None
    audience_limit: Optional[int] = None
    
    # A/B testing preview
    is_ab_test: bool = False
    ab_test_config: Optional[Dict[str, Any]] = None
    
    model_config = {
        "json_encoders": {
            datetime: lambda v: v.isoformat()
        }
    }


class CampaignValidation(BaseModel):
    """Schema for campaign validation"""
    is_valid: bool = True
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    segment_size: Optional[int] = None
    estimated_delivery_time: Optional[str] = None
    template_variables: Optional[List[str]] = None
    missing_variables: Optional[List[str]] = None
    
    # Web Push specific validation
    web_push_delivery_estimate: Optional[Dict[str, Any]] = None
    browser_compatibility: Optional[Dict[str, Any]] = None


class CampaignStats(BaseModel):
    """Schema for campaign statistics"""
    campaign_id: UUID
    name: str
    
    # Delivery metrics
    sent_count: int = 0
    delivered_count: int = 0
    clicked_count: int = 0
    dismissed_count: int = 0
    failed_count: int = 0
    
    # Performance metrics
    delivery_rate: float = 0  # delivered / sent
    click_rate: float = 0     # clicked / delivered
    dismiss_rate: float = 0   # dismissed / delivered
    
    # Time metrics
    avg_time_to_open: Optional[float] = None  # average time in seconds from delivery to click
    avg_time_to_deliver: Optional[float] = None  # average time in seconds from send to delivery
    
    # Browser metrics
    metrics_by_browser: Dict[str, Dict[str, Any]] = Field(default_factory=dict)
    metrics_by_os: Dict[str, Dict[str, Any]] = Field(default_factory=dict)
    metrics_by_device: Dict[str, Dict[str, Any]] = Field(default_factory=dict)
    
    # A/B test metrics (if applicable)
    ab_test_results: Optional[Dict[str, Any]] = None
    
    model_config = {"from_attributes": True}
