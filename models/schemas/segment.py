"""Schemas for segment data"""
import enum
from datetime import datetime
from typing import Dict, Any, Optional, List
from uuid import UUID

from pydantic import BaseModel, Field


class SegmentType(str, enum.Enum):
    """Segment type enum"""
    DYNAMIC = "dynamic"
    STATIC = "static"


class SegmentOperator(str, enum.Enum):
    """Operators for segment filter criteria"""
    EQUALS = "equals"
    NOT_EQUALS = "not_equals"
    GREATER_THAN = "greater_than"
    LESS_THAN = "less_than"
    CONTAINS = "contains"
    NOT_CONTAINS = "not_contains"
    STARTS_WITH = "starts_with"
    ENDS_WITH = "ends_with"
    EXISTS = "exists"
    NOT_EXISTS = "not_exists"
    IN = "in"
    NOT_IN = "not_in"
    BETWEEN = "between"


class CompositeOperator(str, enum.Enum):
    """Operators for combining segments"""
    UNION = "union"          # Users in any of the segments
    INTERSECTION = "intersection"  # Users in all of the segments
    DIFFERENCE = "difference"     # Users in first segment but not in others


class Criterion(BaseModel):
    """Schema for a single filter criterion"""
    field: str
    operator: str
    value: Any
    metadata: Dict[str, Any] = Field(default_factory=dict)


class SegmentRule(BaseModel):
    """Schema for segment filter rules"""
    conditions: List[Criterion] = Field(default_factory=list)
    operator: str = "and"
    metadata: Dict[str, Any] = Field(default_factory=dict)


class CompositeRule(BaseModel):
    """Schema for composite segment rules that combine multiple segments"""
    segment_ids: List[str] = Field(default_factory=list)
    operator: CompositeOperator = CompositeOperator.UNION


class Segment(BaseModel):
    """Schema for segment data"""
    id: Optional[str] = None
    name: str
    description: Optional[str] = None
    segment_type: SegmentType = SegmentType.DYNAMIC
    filter_criteria: Dict[str, Any] = Field(default_factory=dict)
    user_count: int = 0
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    last_evaluated_at: Optional[datetime] = None
    is_active: bool = True
    
    model_config = {"from_attributes": True}


class SegmentCreate(BaseModel):
    """Schema for creating a segment"""
    name: str = Field(..., description="Segment name")
    description: Optional[str] = Field(None, description="Segment description")
    segment_type: SegmentType = Field(SegmentType.DYNAMIC, description="Segment type")
    filter_criteria: Dict[str, Any] = Field(default_factory=dict, description="Filter criteria")


class SegmentUpdate(BaseModel):
    """Schema for updating a segment"""
    name: Optional[str] = Field(None, description="Segment name")
    description: Optional[str] = Field(None, description="Segment description")
    segment_type: Optional[SegmentType] = Field(None, description="Segment type")
    filter_criteria: Optional[Dict[str, Any]] = Field(None, description="Filter criteria")
    is_active: Optional[bool] = Field(None, description="Is the segment active")


class SegmentRead(BaseModel):
    """Schema for reading a segment"""
    id: UUID
    name: str
    description: Optional[str]
    segment_type: SegmentType
    filter_criteria: Dict[str, Any]
    user_count: int
    created_at: datetime
    updated_at: Optional[datetime]
    last_evaluated_at: Optional[datetime]
    is_active: bool


class SegmentList(BaseModel):
    """Schema for listing segments with pagination"""
    items: List[SegmentRead]
    total: int
    page: int = 0
    page_size: int = 100


class SegmentEvaluation(BaseModel):
    """Schema for segment evaluation results"""
    segment_id: str
    user_count: int
    evaluation_time: datetime = Field(default_factory=datetime.now)
    sample_users: Optional[List[str]] = Field(default_factory=list)
    filter_match_counts: Dict[str, int] = Field(default_factory=dict)
    evaluation_metrics: Dict[str, Any] = Field(default_factory=dict)
    is_valid: bool = True
    errors: List[str] = Field(default_factory=list)


class SegmentUserBatch(BaseModel):
    """Schema for adding/removing users to/from static segments in batches"""
    segment_id: str
    user_ids: List[str] = Field(..., description="List of user IDs to add or remove")
    operation: str = Field(..., description="Operation to perform: 'add' or 'remove'")


class SegmentStats(BaseModel):
    """Schema for segment statistics"""
    total: int = 0
    active: int = 0
    dynamic: int = 0
    static: int = 0
    users_per_segment_avg: float = 0
    most_used_attribute: Optional[str] = None
    recently_modified: List[Dict[str, Any]] = Field(default_factory=list)
    growth_data: Dict[str, Any] = Field(default_factory=dict)
    evaluation_data: Dict[str, Any] = Field(default_factory=dict)
