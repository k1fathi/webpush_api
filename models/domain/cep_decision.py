import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, ENUM

from db.base_class import Base
from models.cep_decision import DecisionStatus

class CepDecisionModel(Base):
    """Model for storing CEP (Complex Event Processing) decisions"""
    __tablename__ = "cep_decisions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    campaign_id = Column(UUID(as_uuid=True), ForeignKey("campaigns.id"), nullable=True)
    decision_time = Column(DateTime, default=datetime.utcnow)
    selected_channel = Column(String, nullable=False)
    score = Column(Float, nullable=False)
    decision_factors = Column(JSON, default=dict)
    status = Column(
        ENUM(DecisionStatus, name="decision_status_enum", create_type=False),
        default=DecisionStatus.CREATED
    )
    outcome = Column(JSON, nullable=True)
    
    # Relationships
    user = relationship("UserModel", back_populates="cep_decisions")
    campaign = relationship("CampaignModel", back_populates="cep_decisions")
