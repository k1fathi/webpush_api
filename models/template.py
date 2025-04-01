import uuid
from datetime import datetime
from typing import Dict, Optional
from pydantic import BaseModel, Field, HttpUrl

class Template(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    title: str
    body: str
    image_url: Optional[HttpUrl] = None
    action_url: Optional[HttpUrl] = None
    dynamic_variables: Dict = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    class Config:
        orm_mode = True
