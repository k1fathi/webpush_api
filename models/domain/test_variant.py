import uuid
from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID

from db.base_class import Base

class TestVariantModel(Base):
    """Test variant model for A/B testing"""
    __tablename__ = "test_variants"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ab_test_id = Column(UUID(as_uuid=True), ForeignKey("ab_tests.id"), nullable=False)
    template_id = Column(UUID(as_uuid=True), ForeignKey("templates.id"), nullable=False)
    name = Column(String, nullable=False)
    sent_count = Column(Integer, default=0)
    opened_count = Column(Integer, default=0)
    clicked_count = Column(Integer, default=0)
    
    # Relationships
    ab_test = relationship("AbTestModel", back_populates="variants")
    template = relationship("TemplateModel")
