import uuid
import enum
from datetime import datetime
from typing import Dict, List, Optional, Any, Union

from pydantic import BaseModel, Field

class SegmentType(str, enum.Enum):
    """Types of segments"""
    STATIC = "static"       # Manually defined list of users
    DYNAMIC = "dynamic"     # Rule-based segment that's evaluated at runtime
    BEHAVIORAL = "behavioral"  # Based on user behavior/actions
    COMPOSITE = "composite" # Combination of other segments (union, intersection)

class SegmentOperator(str, enum.Enum):
    """Operators for segment criteria"""
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
    """Operators for composite segments"""
    UNION = "union"           # OR logic
    INTERSECTION = "intersection"  # AND logic
    DIFFERENCE = "difference"   # Exclude B from A

class Criterion(BaseModel):
    """Single criterion for segment filtering"""
    field: str
    operator: SegmentOperator
    value: Any = None

class SegmentRule(BaseModel):
    """Rule for segment filtering, can contain multiple criteria"""
    criteria: List[Criterion]
    operator: str = "AND"  # Can be "AND" or "OR"

class CompositeRule(BaseModel):
    """Rule for composite segments"""
    segment_ids: List[str]
    operator: CompositeOperator

class Segment(BaseModel):
    """Model representing a user segment"""
    id: Optional[str] = None
    name: str
    description: Optional[str] = None
    segment_type: SegmentType
    filter_criteria: Optional[Dict[str, Any]] = Field(default_factory=dict)
    rules: Optional[List[SegmentRule]] = None
    composite_rule: Optional[CompositeRule] = None
    user_count: int = 0
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    last_evaluated_at: Optional[datetime] = None
    is_active: bool = True
    
    model_config = {"from_attributes": True}

class SegmentBase(BaseModel):
    """Base schema for segments"""
    name: str
    description: Optional[str] = None
    segment_type: SegmentType = SegmentType.DYNAMIC
    is_active: bool = True
    
    model_config = {
        "from_attributes": True
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
