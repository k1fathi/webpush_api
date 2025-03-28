from pydantic import BaseModel, HttpUrl, validator
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class NotificationPriority(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"

class NotificationType(str, Enum):
    time_based = "time_based"
    trigger_based = "trigger_based"

class ActionCreate(BaseModel):
    type: str
    title: str
    action: str

class ScheduleCreate(BaseModel):
    type: NotificationType
    trigger_type: Optional[str]
    trigger_conditions: Optional[Dict[str, Any]]
    send_at: Optional[datetime]

class TrackingCreate(BaseModel):
    enable_delivery_tracking: bool = True
    enable_open_tracking: bool = True
    enable_click_tracking: bool = True
    utm_params: Optional[Dict[str, str]]

class SegmentCondition(BaseModel):
    loyalty_tier: Optional[str]
    last_purchase: Optional[str]
    country: Optional[str]
    custom_rules: Optional[Dict[str, Any]]

class SegmentCreate(BaseModel):
    name: str
    conditions: SegmentCondition

class Variables(BaseModel):
    name: str
    product: str
    time: str
    link: str

class NotificationDataCreate(BaseModel):
    deep_link: Optional[str]
    campaign_id: Optional[str]
    variables: Variables

class CEPStrategyCreate(BaseModel):
    channel_priority: List[str]
    optimal_time: str

class CDPProfile(BaseModel):
    loyalty_tier: str
    last_purchase: str

class CDPDataCreate(BaseModel):
    user_id: str
    profile: CDPProfile

class WebhookUrls(BaseModel):
    delivery: Optional[str]
    click: Optional[str]
    conversion: Optional[str]

class TargetingRules(BaseModel):
    country: Optional[str]
    last_activity: Optional[str]
    purchase_history: Optional[str]

class NotificationCreate(BaseModel):
    title: str
    body: str
    icon: Optional[HttpUrl]
    image: Optional[HttpUrl]
    badge: Optional[str]
    data: Optional[Dict[str, Any]]
    priority: NotificationPriority = NotificationPriority.medium
    ttl: Optional[int]
    require_interaction: bool = False
    variant_id: Optional[str]
    ab_test_group: Optional[str]
    schedule: Optional[ScheduleCreate]
    tracking: Optional[TrackingCreate]
    actions: Optional[List[ActionCreate]]
    segments: Optional[List[SegmentCreate]]
    data: Optional[NotificationDataCreate]
    cep_strategy: Optional[CEPStrategyCreate]
    cdp_data: Optional[CDPDataCreate]
    targeting_rules: Optional[TargetingRules]
    webhooks: Optional[WebhookUrls]

class NotificationResponse(NotificationCreate):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True

class TemplateCreate(BaseModel):
    name: str
    title_template: str
    body_template: str
    variables: List[str]
    category: str

class TemplateResponse(TemplateCreate):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True

class CampaignCreate(BaseModel):
    name: str
    template_id: int
    start_date: datetime
    end_date: Optional[datetime]
    segments: List[str]
    schedule_type: str  # immediate, scheduled, trigger-based
    trigger_conditions: Optional[Dict[str, Any]]

class CampaignResponse(BaseModel):
    id: int
    name: str
    template_id: int
    status: Optional[str]
    start_date: datetime
    end_date: Optional[datetime]
    schedule_type: str
    trigger_conditions: Optional[Dict[str, Any]]
    created_at: datetime
    segments: List[str] = []

    @validator('segments', pre=True)
    def extract_segment_names(cls, v, values):
        if isinstance(v, list) and len(v) > 0 and hasattr(v[0], 'segment_name'):
            return [segment.segment_name for segment in v]
        return v

    class Config:
        orm_mode = True

class TriggerCreate(BaseModel):
    name: str
    event_type: str
    conditions: Dict[str, Any]
    linked_campaign_id: str

class ABTestCreate(BaseModel):
    campaign_id: str
    variants: List[Dict[str, str]]
    test_duration: str

class WebhookCreate(BaseModel):
    url: HttpUrl
    events: List[str]
    secret: Optional[str]

class CDPProfileSync(BaseModel):
    user_id: str
    profile: Dict[str, Any]

class DashboardMetrics(BaseModel):
    ctr: float
    conversion_rate: float
    delivery_rate: Optional[float]
    total_sent: Optional[int]

class SegmentPerformance(BaseModel):
    segment_name: str
    metrics: DashboardMetrics

class DeliveryStatusResponse(BaseModel):
    notification_id: int
    total_sent: int
    delivered: int
    failed: int
    clicked: int
    conversion_rate: float
    
    class Config:
        orm_mode = True

class CampaignAnalytics(BaseModel):
    deliveries: int = 0
    clicks: int = 0
    opens: int = 0
    conversions: int = 0
    
    @property
    def click_rate(self) -> float:
        return (self.clicks / self.deliveries * 100) if self.deliveries > 0 else 0
    
    @property
    def open_rate(self) -> float:
        return (self.opens / self.deliveries * 100) if self.deliveries > 0 else 0

class AnalyticsResponse(BaseModel):
    campaign_id: int
    start_date: datetime
    end_date: datetime
    total_sent: int
    metrics: CampaignAnalytics
    segment_performance: Dict[str, Dict[str, float]]
    ab_test_results: Optional[Dict[str, Any]] = None

    class Config:
        orm_mode = True

class UserCreate(BaseModel):
    name: str
    email: str
    birthday: Optional[datetime]
    device_token: Optional[str]

class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    last_login: Optional[datetime]
    membership_date: datetime
    is_subscribed: bool
    segments: List[str] = []

    class Config:
        orm_mode = True

class DeliveryReportResponse(BaseModel):
    notification_id: int
    delivered: bool
    delivered_time: Optional[datetime]
    open_rate: float
    click_rate: float

    class Config:
        orm_mode = True
