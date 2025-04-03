import uuid
from pydantic import BaseModel, Field

class TestVariant(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    ab_test_id: str
    template_id: str
    name: str
    sent_count: int = 0
    opened_count: int = 0
    clicked_count: int = 0
    
    model_config = {"from_attributes": True}  # Updated from orm_mode for Pydantic v2
