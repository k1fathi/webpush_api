import datetime
import uuid
from sqlalchemy import Column, String, Float, JSON, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from db.base_class import Base

class CepDecisionModel(Base):
    """SQLAlchemy model for CEP decisions"""
    __tablename__ = "cep_decisions"
    
    # Use UUID type directly with as_uuid=True parameter
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Foreign keys must be the same type as their referenced columns
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    campaign_id = Column(UUID(as_uuid=True), ForeignKey("campaigns.id"), nullable=False)
    
    # Rest of the columns
    decision_time = Column(DateTime, default=datetime.datetime.utcnow)
    selected_channel = Column(String(50), nullable=False)
    score = Column(Float, nullable=False, default=0.0)
    factors = Column(JSON, nullable=False, default={})
    alternative_channels = Column(JSON, nullable=False, default=[])
    
    # Add standard timestamp columns
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    # Relationships
    user = relationship("UserModel", back_populates="cep_decisions")
    campaign = relationship("CampaignModel", back_populates="cep_decisions")
    
    def __repr__(self):
        return f"<CepDecision(id={self.id}, user_id={self.user_id}, campaign_id={self.campaign_id}, channel={self.selected_channel})>"
