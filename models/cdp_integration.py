import uuid
from datetime import datetime
from typing import Dict
from pydantic import BaseModel, Field

class CdpIntegration(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    user_profile_data: Dict = Field(default_factory=dict)
    behavioral_data: Dict = Field(default_factory=dict)
    last_synced: datetime = Field(default_factory=datetime.now)
    
    model_config = {"from_attributes": True}  # Updated from orm_mode for Pydantic v2
