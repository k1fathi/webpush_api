import uuid
from datetime import datetime
from sqlalchemy import Boolean, Column, String, Integer, DateTime, Text, JSON
from sqlalchemy.dialects.postgresql import UUID, ENUM

from db.base_class import Base
from models.segment import SegmentType

class SegmentModel(Base):
    """Segment model for storing user segments"""
    __tablename__ = "segments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    description = Column(Text)
    segment_type = Column(
        ENUM(SegmentType, name="segment_type_enum", create_type=False),
        default=SegmentType.DYNAMIC
    )
    filter_criteria = Column(JSON, default=dict)
    user_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_evaluated_at = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)
