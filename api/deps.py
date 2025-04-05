from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from typing import Dict, Any

from core.config import settings
from repositories.trigger import TriggerRepository
from services.trigger import TriggerService
from repositories.webhook import WebhookRepository
from services.webhook import WebhookService
from repositories.notification import NotificationRepository
from services.notification_delivery import NotificationDeliveryService

# Create OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_PREFIX}/users/token")

async def get_current_user(token: str = Depends(oauth2_scheme)) -> Dict[str, Any]:
    """
    Get current user from token (simplified mock for development)
    """
    # In production, this would verify the token
    # For development, just return a mock user
    return {
        "id": "dev-user-id",
        "email": "dev@example.com",
        "is_active": True,
        "is_superuser": True
    }

async def get_current_active_user(current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
    """
    Check if current user is active
    """
    if not current_user.get("is_active", False):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Inactive user"
        )
    return current_user

def get_trigger_repository():
    """Get trigger repository"""
    return TriggerRepository()

def get_trigger_service():
    """Get trigger service"""
    repository = get_trigger_repository()
    return TriggerService(repository)

def get_webhook_repository():
    """Get webhook repository"""
    return WebhookRepository()

def get_webhook_service():
    """Get webhook service"""
    repository = get_webhook_repository()
    return WebhookService(repository)

def get_notification_repository():
    """Get notification repository"""
    return NotificationRepository()

def get_notification_delivery_service():
    """Get notification delivery service"""
    notification_repo = get_notification_repository()
    return NotificationDeliveryService(notification_repo)
