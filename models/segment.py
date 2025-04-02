import uuid
import enum
from datetime import datetime
from typing import Dict, List, Optional, Any
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
    
    class Config:
        orm_mode = True
