import uuid
from datetime import datetime
from sqlalchemy import Column, String, JSON, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID

from db.session import Base
from models.cdp_integration import CdpSyncStatus


class CdpIntegrationModel(Base):
    """CDP integration model for database storage"""
    __tablename__ = "cdp_integrations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    user_profile_data = Column(JSON, default=dict)
    behavioral_data = Column(JSON, default=dict)
    last_synced = Column(DateTime, nullable=True)
    sync_status = Column(
        Enum(CdpSyncStatus, name="cdp_sync_status", create_type=False),
        default=CdpSyncStatus.PENDING
    )
    error_message = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("UserModel")
    
    def __repr__(self):
        return f"<CdpIntegration user_id={self.user_id}, sync_status={self.sync_status}>"
