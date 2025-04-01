from pydantic import BaseModel, HttpUrl
from typing import Optional, Dict, Any
from datetime import datetime

class WebPushBase(BaseModel):
    title: str
    body: str
    icon: Optional[HttpUrl] = None
    image: Optional[HttpUrl] = None
    deep_link: Optional[str] = None
    data: Optional[Dict[str, Any]] = None

class WebPushCreate(WebPushBase):
    user_id: int
    template_id: Optional[int] = None
    campaign_id: Optional[int] = None
    trigger_id: Optional[int] = None

class WebPushUpdate(BaseModel):
    status: Optional[str] = None
    delivered_at: Optional[datetime] = None
    clicked_at: Optional[datetime] = None

class WebPushResponse(WebPushBase):
    webpush_id: int
    status: str
    sent_at: Optional[datetime]
    delivered_at: Optional[datetime]
    clicked_at: Optional[datetime]
    
    class Config:
        orm_mode = True
