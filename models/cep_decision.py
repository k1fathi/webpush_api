import uuid
from datetime import datetime
from enum import Enum
from typing import Dict
from pydantic import BaseModel, Field

class ChannelType(str, Enum):
    WEBPUSH = "webpush"
    EMAIL = "email"
    SMS = "sms"
    WHATSAPP = "whatsapp"
    IN_APP = "in_app"

class CepDecision(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    campaign_id: str
    selected_channel: ChannelType = ChannelType.WEBPUSH
    channel_score: float
    decision_factors: Dict = Field(default_factory=dict)
    decision_time: datetime = Field(default_factory=datetime.now)
    
    class Config:
        orm_mode = True
