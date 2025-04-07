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
