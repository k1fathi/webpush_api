import uuid
from datetime import datetime
from typing import Dict, List, Optional
from pydantic import BaseModel, Field, EmailStr

class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    email: EmailStr
    subscription_date: datetime = Field(default_factory=datetime.now)
    browser: Optional[str] = None
    device_info: Optional[str] = None
    push_token: Optional[str] = None
    opted_in: bool = True
    last_activity: Optional[datetime] = None
    custom_attributes: Dict = Field(default_factory=dict)
    
    class Config:
        orm_mode = True
