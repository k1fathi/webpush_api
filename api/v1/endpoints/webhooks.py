from fastapi import APIRouter, Depends, HTTPException, Query, status
from typing import List, Optional

from models.schemas.webhook import (
    WebhookCreate, WebhookRead, WebhookUpdate, WebhookList, WebhookEventType
)
from services.webhook import WebhookService
from api.deps import get_current_user, get_webhook_service

router = APIRouter()

@router.get("/", response_model=WebhookList)
async def list_webhooks(
    skip: int = 0,
    limit: int = 100,
    event_type: Optional[WebhookEventType] = None,
    is_active: Optional[bool] = None,
    service: WebhookService = Depends(get_webhook_service),
    current_user = Depends(get_current_user)
):
    """
    List all webhooks with optional filtering
    """
    return await service.list_webhooks(
        skip=skip, 
        limit=limit,
        event_type=event_type,
        is_active=is_active
    )

@router.post("/", response_model=WebhookRead, status_code=status.HTTP_201_CREATED)
async def create_webhook(
    webhook: WebhookCreate,
    service: WebhookService = Depends(get_webhook_service),
    current_user = Depends(get_current_user)
):
    """
    Create a new webhook
    """
    return await service.create_webhook(webhook)

@router.get("/{webhook_id}", response_model=WebhookRead)
async def get_webhook(
    webhook_id: str,
    service: WebhookService = Depends(get_webhook_service),
    current_user = Depends(get_current_user)
):
    """
    Get a specific webhook by ID
    """
    webhook = await service.get_webhook(webhook_id)
    if not webhook:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Webhook not found"
        )
    return webhook

@router.put("/{webhook_id}", response_model=WebhookRead)
async def update_webhook(
    webhook_id: str,
    webhook_update: WebhookUpdate,
    service: WebhookService = Depends(get_webhook_service),
    current_user = Depends(get_current_user)
):
    """
    Update a webhook
    """
    updated_webhook = await service.update_webhook(webhook_id, webhook_update)
    if not updated_webhook:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Webhook not found"
        )
    return updated_webhook

@router.delete("/{webhook_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_webhook(
    webhook_id: str,
    service: WebhookService = Depends(get_webhook_service),
    current_user = Depends(get_current_user)
):
    """
    Delete a webhook
    """
    deleted = await service.delete_webhook(webhook_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Webhook not found"
        )

@router.post("/{webhook_id}/activate", response_model=WebhookRead)
async def activate_webhook(
    webhook_id: str,
    service: WebhookService = Depends(get_webhook_service),
    current_user = Depends(get_current_user)
):
    """
    Activate a webhook
    """
    webhook = await service.activate_webhook(webhook_id)
    if not webhook:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Webhook not found"
        )
    return webhook

@router.post("/{webhook_id}/deactivate", response_model=WebhookRead)
async def deactivate_webhook(
    webhook_id: str,
    service: WebhookService = Depends(get_webhook_service),
    current_user = Depends(get_current_user)
):
    """
    Deactivate a webhook
    """
    webhook = await service.deactivate_webhook(webhook_id)
    if not webhook:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Webhook not found"
        )
    return webhook

@router.post("/{webhook_id}/test", status_code=status.HTTP_200_OK)
async def test_webhook(
    webhook_id: str,
    service: WebhookService = Depends(get_webhook_service),
    current_user = Depends(get_current_user)
):
    """
    Test a webhook by sending a test payload
    """
    success, message = await service.test_webhook(webhook_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message
        )
    return {"status": "success", "message": message}
