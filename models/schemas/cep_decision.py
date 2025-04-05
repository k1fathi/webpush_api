import enum
from datetime import datetime
from enum import Enum
from typing import Dict, Optional, Any, List

from pydantic import BaseModel, Field

class DecisionStatus(str, enum.Enum):
    """Status of a CEP decision"""
    CREATED = "created"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"

class ChannelType(str, Enum):
    """Channel types for CEP decisions"""
    EMAIL = "email"
    SMS = "sms"
    WEBPUSH = "webpush"
    MOBILE_PUSH = "mobile_push"
    IN_APP = "in_app"
    WHATSAPP = "whatsapp"
    SOCIAL = "social"
    OTHER = "other"

class DecisionFactor(BaseModel):
    """Factor used in channel decision-making"""
    name: str
    weight: float
    score: float
    description: Optional[str] = None

class CepDecision(BaseModel):
    """
    Model for Customer Engagement Platform channel decisions
    Tracks which channel was selected for a user and campaign
    """
    id: Optional[str] = None
    user_id: str
    campaign_id: str
    selected_channel: ChannelType
    score: float = 0.0
    factors: Dict[str, Any] = Field(default_factory=dict)
    alternative_channels: List[Dict[str, Any]] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.now)
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "user_id": "12345",
                "campaign_id": "campaign123",
                "selected_channel": "webpush",
                "score": 0.85,
                "factors": {
                    "channel_preference": 0.9,
                    "previous_engagement": 0.8,
                    "time_of_day": 0.7
                },
                "alternative_channels": [
                    {"channel": "email", "score": 0.75},
                    {"channel": "sms", "score": 0.6}
                ]
            }
        }
    }

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
