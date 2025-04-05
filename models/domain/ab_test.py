import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, ENUM

from db.base_class import Base
from models.schemas.ab_test import WinningCriteria

class AbTestModel(Base):
    """A/B test model"""
    __tablename__ = "ab_tests"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    campaign_id = Column(UUID(as_uuid=True), ForeignKey("campaigns.id"), nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    variant_count = Column(Integer, default=2)
    winning_criteria = Column(
        ENUM(WinningCriteria, name="winning_criteria_enum", create_type=False),
        default=WinningCriteria.CLICK_RATE
    )
    start_date = Column(DateTime, nullable=True)
    end_date = Column(DateTime, nullable=True)
    
    # Relationships
    campaign = relationship("CampaignModel", back_populates="ab_tests")
    variants = relationship("TestVariantModel", back_populates="ab_test", cascade="all, delete-orphan")
