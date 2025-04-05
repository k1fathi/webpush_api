import uuid
from typing import Optional

from pydantic import BaseModel, Field

class TestVariant(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    ab_test_id: str
    template_id: str
    name: str
    sent_count: int = 0
    opened_count: int = 0
    clicked_count: int = 0
    
    model_config = {"from_attributes": True}

class TestVariantBase(BaseModel):
    """Base schema for test variants"""
    name: str
    template_id: str
    
    model_config = {
        "from_attributes": True
    }

class TestVariantCreate(TestVariantBase):
    """Schema for creating test variants"""
    pass

class TestVariantUpdate(BaseModel):
    """Schema for updating test variants"""
    name: Optional[str] = None
    template_id: Optional[str] = None
    sent_count: Optional[int] = None
    opened_count: Optional[int] = None
    clicked_count: Optional[int] = None

class TestVariantRead(TestVariantBase):
    """Schema for reading test variants"""
    id: str
    ab_test_id: str
    sent_count: int = 0
    opened_count: int = 0
    clicked_count: int = 0
    
    model_config = {
        "from_attributes": True
    }
