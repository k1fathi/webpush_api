from fastapi import APIRouter, Depends, HTTPException, Query, status
from typing import List, Optional

from models.schemas.trigger import (
    TriggerCreate, TriggerRead, TriggerUpdate, TriggerList, 
    TriggerEvent, TriggerResult
)
from services.trigger import TriggerService
from api.deps import get_current_user, get_trigger_service

router = APIRouter()

@router.get("/", response_model=TriggerList)
async def list_triggers(
    skip: int = 0,
    limit: int = 100,
    trigger_type: Optional[str] = None,
    status: Optional[str] = None,
    service: TriggerService = Depends(get_trigger_service),
    current_user = Depends(get_current_user)
):
    """
    List all triggers with optional filtering
    """
    return await service.list_triggers(
        skip=skip, 
        limit=limit,
        trigger_type=trigger_type,
        status=status
    )

@router.post("/", response_model=TriggerRead, status_code=status.HTTP_201_CREATED)
async def create_trigger(
    trigger: TriggerCreate,
    service: TriggerService = Depends(get_trigger_service),
    current_user = Depends(get_current_user)
):
    """
    Create a new trigger
    """
    return await service.create_trigger(trigger)

@router.get("/{trigger_id}", response_model=TriggerRead)
async def get_trigger(
    trigger_id: str,
    service: TriggerService = Depends(get_trigger_service),
    current_user = Depends(get_current_user)
):
    """
    Get a specific trigger by ID
    """
    trigger = await service.get_trigger(trigger_id)
    if not trigger:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trigger not found"
        )
    return trigger

@router.put("/{trigger_id}", response_model=TriggerRead)
async def update_trigger(
    trigger_id: str,
    trigger_update: TriggerUpdate,
    service: TriggerService = Depends(get_trigger_service),
    current_user = Depends(get_current_user)
):
    """
    Update a trigger
    """
    updated_trigger = await service.update_trigger(trigger_id, trigger_update)
    if not updated_trigger:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trigger not found"
        )
    return updated_trigger

@router.delete("/{trigger_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_trigger(
    trigger_id: str,
    service: TriggerService = Depends(get_trigger_service),
    current_user = Depends(get_current_user)
):
    """
    Delete a trigger
    """
    deleted = await service.delete_trigger(trigger_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trigger not found"
        )

@router.post("/{trigger_id}/activate", response_model=TriggerRead)
async def activate_trigger(
    trigger_id: str,
    service: TriggerService = Depends(get_trigger_service),
    current_user = Depends(get_current_user)
):
    """
    Activate a trigger
    """
    trigger = await service.activate_trigger(trigger_id)
    if not trigger:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trigger not found"
        )
    return trigger

@router.post("/{trigger_id}/deactivate", response_model=TriggerRead)
async def deactivate_trigger(
    trigger_id: str,
    service: TriggerService = Depends(get_trigger_service),
    current_user = Depends(get_current_user)
):
    """
    Deactivate a trigger
    """
    trigger = await service.deactivate_trigger(trigger_id)
    if not trigger:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trigger not found"
        )
    return trigger

@router.post("/events", response_model=List[TriggerResult])
async def process_trigger_event(
    event: TriggerEvent,
    service: TriggerService = Depends(get_trigger_service)
):
    """
    Process a trigger event
    """
    results = await service.process_event(event)
    return results
