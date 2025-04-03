import uuid
from datetime import datetime, timedelta
from sqlalchemy import Column, String, Integer, DateTime, Text, JSON, Boolean, Interval, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, ENUM
from sqlalchemy.orm import relationship

from db.base_class import Base
from models.trigger import TriggerType, TriggerStatus

class TriggerModel(Base):
    """Trigger model for database storage"""
    __tablename__ = "triggers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    description = Column(Text)
    trigger_type = Column(
        ENUM(TriggerType, name="trigger_type_enum", create_type=False),
        nullable=False
    )
    status = Column(
        ENUM(TriggerStatus, name="trigger_status_enum", create_type=False),
        default=TriggerStatus.ACTIVE
    )
    
    # Trigger definition
    rules = Column(JSON, nullable=False)
    schedule = Column(JSON)  # Optional for scheduled triggers
    action = Column(JSON, nullable=False)
    
    # Metadata and tracking
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_triggered_at = Column(DateTime)
    trigger_count = Column(Integer, default=0)
    error_count = Column(Integer, default=0)
    trigger_metadata = Column(JSON, default=dict)  # Renamed from 'metadata' to avoid conflict
    
    # Limits and thresholds
    cooldown_period = Column(Interval)
    max_triggers_per_day = Column(Integer)
    enabled = Column(Boolean, default=True)

    # Relationships
    executions = relationship("TriggerExecutionModel", back_populates="trigger")

class TriggerExecutionModel(Base):
    """Model for tracking trigger executions"""
    __tablename__ = "trigger_executions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    trigger_id = Column(UUID(as_uuid=True), ForeignKey("triggers.id"), nullable=False)
    executed_at = Column(DateTime, default=datetime.utcnow)
    success = Column(Boolean, nullable=False)
    action_result = Column(JSON)
    error = Column(Text)
    
    # Relationships
    trigger = relationship("TriggerModel", back_populates="executions")
