from datetime import datetime
from typing import Dict, List, Optional, Any, Union

from pydantic import BaseModel, Field

from models.segment import SegmentType, SegmentRule, CompositeRule

class SegmentBase(BaseModel):
    """Base schema for segments"""
    name: str
    description: Optional[str] = None
    segment_type: SegmentType = SegmentType.DYNAMIC
    is_active: bool = True
    
    model_config = {
        "from_attributes": True  # Updated from orm_mode = True
    }

class SegmentCreate(SegmentBase):
    """Schema for creating segments"""
    filter_criteria: Dict[str, Any] = Field(default_factory=dict)
    rules: Optional[List[SegmentRule]] = None
    composite_rule: Optional[CompositeRule] = None

class SegmentUpdate(BaseModel):
    """Schema for updating segments"""
    name: Optional[str] = None
    description: Optional[str] = None
    filter_criteria: Optional[Dict[str, Any]] = None
    rules: Optional[List[SegmentRule]] = None
    composite_rule: Optional[CompositeRule] = None
    is_active: Optional[bool] = None

class SegmentRead(SegmentBase):
    """Schema for reading segments"""
    id: str
    filter_criteria: Dict[str, Any]
    rules: Optional[List[SegmentRule]] = None
    composite_rule: Optional[CompositeRule] = None
    user_count: int
    created_at: datetime
    updated_at: datetime
    last_evaluated_at: Optional[datetime] = None
    
    model_config = {
        "from_attributes": True
    }

class SegmentList(BaseModel):
    """Schema for listing segments with pagination"""
    items: List[SegmentRead]
    total: int
    skip: int
    limit: int

class SegmentEvaluation(BaseModel):
    """Schema for segment evaluation results"""
    segment_id: str
    user_count: int
    evaluation_time: datetime
    matched_users: Optional[List[str]] = None
    get_matched_users: bool = False

class SegmentUserBatch(BaseModel):
    """Schema for adding/removing users to/from a segment"""
    user_ids: List[str]

class SegmentStats(BaseModel):
    """Schema for segment statistics"""
    segment_id: str
    user_count: int
    user_growth_rate: float
    campaigns_using: int
    last_updated: datetime
