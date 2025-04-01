import uuid
from datetime import datetime
from typing import Dict, Optional
from pydantic import BaseModel, Field

class Segment(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: Optional[str] = None
    filter_criteria: Dict = Field(default_factory=dict)
    user_count: int = 0
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    class Config:
        orm_mode = True
