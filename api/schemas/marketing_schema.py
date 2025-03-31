from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

class CampaignCreate(BaseModel):
    name: str
    start_time: datetime
    end_time: Optional[datetime]
    segments: List[str]

class CampaignResponse(CampaignCreate):
    campaign_id: int
    status: str
    created_at: datetime
    
    class Config:
        orm_mode = True

class TemplateCreate(BaseModel):
    name: str
    content: str
    variables: List[str]

class TemplateResponse(TemplateCreate):
    template_id: int
    created_at: datetime
    
    class Config:
        orm_mode = True
