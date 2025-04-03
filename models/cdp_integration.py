from datetime import datetime
from enum import Enum
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field


class CdpSyncStatus(str, Enum):
    """Status of CDP synchronization"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    SUCCESS = "success"
    ERROR = "error"
    SKIPPED = "skipped"


class CdpIntegration(BaseModel):
    """Model for CDP integration data"""
    id: str = Field(..., description="Unique identifier")
    user_id: str = Field(..., description="User ID this integration belongs to")
    user_profile_data: Dict[str, Any] = Field(default_factory=dict, description="User profile data from CDP")
    behavioral_data: Dict[str, Any] = Field(default_factory=dict, description="Behavioral data from CDP")
    last_synced: Optional[datetime] = Field(None, description="Last sync timestamp")
    sync_status: CdpSyncStatus = Field(default=CdpSyncStatus.PENDING, description="Sync status")
    error_message: Optional[str] = Field(None, description="Error message if sync failed")
    
    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "user_id": "123e4567-e89b-12d3-a456-426614174000",
                "user_profile_data": {
                    "segments": ["high_value", "active"],
                    "scores": {"engagement": 85, "churn_risk": 12}
                },
                "last_synced": "2023-09-15T10:30:00Z",
                "sync_status": "success"
            }
        }
    }


class CdpIntegrationCreate(BaseModel):
    """Model for creating CDP integration"""
    user_id: str
    user_profile_data: Optional[Dict[str, Any]] = None
    behavioral_data: Optional[Dict[str, Any]] = None


class CdpIntegrationUpdate(BaseModel):
    """Model for updating CDP integration"""
    user_profile_data: Optional[Dict[str, Any]] = None
    behavioral_data: Optional[Dict[str, Any]] = None
    last_synced: Optional[datetime] = None
    sync_status: Optional[CdpSyncStatus] = None
    error_message: Optional[str] = None


class CdpIntegrationRead(CdpIntegration):
    """Model for reading CDP integration"""
    pass


class CdpEvent(BaseModel):
    """Model for CDP events"""
    user_id: str
    event_type: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    properties: Dict[str, Any] = Field(default_factory=dict)
    context: Dict[str, Any] = Field(default_factory=dict)

    model_config = {
        "json_schema_extra": {
            "example": {
                "user_id": "123e4567-e89b-12d3-a456-426614174000",
                "event_type": "notification_clicked",
                "timestamp": "2023-09-15T10:30:00Z",
                "properties": {
                    "notification_id": "550e8400-e29b-41d4-a716-446655440000",
                    "campaign_id": "7f9c2d6a-8e7b-4f0c-9d1e-5a2b3c8d9e0f"
                },
                "context": {
                    "device": "mobile",
                    "platform": "ios"
                }
            }
        }
    }
