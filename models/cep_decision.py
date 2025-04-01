import enum
from datetime import datetime
from typing import Dict, Optional, Any, List

from pydantic import BaseModel, Field, validator

class DecisionStatus(str, enum.Enum):
    """Status of a CEP decision"""
    CREATED = "created"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"

class ChannelType(str, Enum):
    WEBPUSH = "webpush"
    EMAIL = "email"
    SMS = "sms"
    WHATSAPP = "whatsapp"
    IN_APP = "in_app"

class CepDecision(BaseModel):
    """
    Model for storing CEP (Complex Event Processing) decisions
    These decisions determine the optimal communication channel and timing
    """
    id: Optional[str] = None
    user_id: str
    campaign_id: Optional[str] = None
    decision_time: datetime = Field(default_factory=datetime.now)
    selected_channel: str
    score: float
    decision_factors: Dict[str, Any] = Field(default_factory=dict)
    status: DecisionStatus = DecisionStatus.CREATED
    outcome: Optional[Dict[str, Any]] = None
    
    class Config:
        orm_mode = True
        
    @validator('selected_channel')
    def channel_must_be_valid(cls, v):
        valid_channels = ["webpush", "email", "sms", "in_app", "mobile_push"]
        if v not in valid_channels:
            raise ValueError(f"Channel must be one of: {', '.join(valid_channels)}")
        return v

class ChannelScore(BaseModel):
    """Score for a communication channel"""
    channel: str
    score: float
    factors: Dict[str, Any] = Field(default_factory=dict)

class CepDecisionCreate(BaseModel):
    """Schema for creating a CEP decision"""
    user_id: str
    campaign_id: Optional[str] = None
    selected_channel: str
    score: float
    decision_factors: Dict[str, Any] = Field(default_factory=dict)

class CepDecisionUpdate(BaseModel):
    """Schema for updating a CEP decision"""
    status: Optional[DecisionStatus] = None
    outcome: Optional[Dict[str, Any]] = None

class CepDecisionRead(CepDecision):
    """Schema for reading a CEP decision"""
    pass
