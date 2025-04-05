import logging
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

# Optional import for croniter with fallback
try:
    from croniter import croniter
except ImportError:
    croniter = None
    logging.warning("croniter module not found. Scheduled triggers with cron expressions will not work properly.")

from fastapi.encoders import jsonable_encoder
from fastapi import HTTPException, status

from core.config import settings
from models.schemas.trigger import (
    Trigger, TriggerStatus, TriggerType, TriggerAction,
    ScheduleConfig, ActionConfig, TriggerCreate, TriggerRead, TriggerUpdate, TriggerList,
    TriggerEvent, TriggerResult
)
from repositories.trigger import TriggerRepository
from repositories.notification import NotificationRepository
from repositories.campaign import CampaignRepository
from repositories.segment import SegmentRepository
from utils.audit import audit_log

logger = logging.getLogger(__name__)

class TriggerService:
    """Service for managing notification triggers"""
    
    def __init__(self, repository: TriggerRepository):
        self.repository = repository
    
    async def create_trigger(self, trigger_create: TriggerCreate) -> TriggerRead:
        """Create a new trigger"""
        # Convert timedelta to seconds for storage
        cooldown_seconds = None
        if trigger_create.cooldown_period is not None:
            cooldown_seconds = trigger_create.cooldown_period
        
        # Create trigger object
        trigger = Trigger(
            name=trigger_create.name,
            description=trigger_create.description,
            trigger_type=trigger_create.trigger_type,
            rules=trigger_create.rules,
            schedule=trigger_create.schedule,
            action=trigger_create.action,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            status=TriggerStatus.ACTIVE,
            cooldown_period=timedelta(seconds=cooldown_seconds) if cooldown_seconds else None,
            max_triggers_per_day=trigger_create.max_triggers_per_day,
            metadata=trigger_create.metadata,
            enabled=True
        )
        
        # Save to database
        created_trigger = await self.repository.create(trigger)
        return TriggerRead.model_validate(created_trigger)
    
    async def get_trigger(self, trigger_id: str) -> Optional[TriggerRead]:
        """Get a trigger by ID"""
        trigger = await self.repository.get(trigger_id)
        if not trigger:
            return None
        return TriggerRead.model_validate(trigger)
    
    async def update_trigger(self, trigger_id: str, trigger_update: TriggerUpdate) -> Optional[TriggerRead]:
        """Update a trigger"""
        # First get existing trigger
        trigger = await self.repository.get(trigger_id)
        if not trigger:
            return None
        
        # Update fields
        update_data = trigger_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            if key == "cooldown_period" and value is not None:
                setattr(trigger, key, timedelta(seconds=value))
            else:
                setattr(trigger, key, value)
        
        # Always update the updated_at field
        trigger.updated_at = datetime.now()
        
        # Save to database
        updated_trigger = await self.repository.update(trigger_id, trigger)
        return TriggerRead.model_validate(updated_trigger)
    
    async def delete_trigger(self, trigger_id: str) -> bool:
        """Delete a trigger"""
        return await self.repository.delete(trigger_id)
    
    async def list_triggers(
        self, 
        skip: int = 0, 
        limit: int = 100,
        trigger_type: Optional[str] = None,
        status: Optional[str] = None
    ) -> TriggerList:
        """List all triggers with filtering options"""
        filters = {}
        if trigger_type:
            filters["trigger_type"] = trigger_type
        if status:
            filters["status"] = status
            
        triggers = await self.repository.list(
            skip=skip,
            limit=limit,
            filters=filters
        )
        total = await self.repository.count(filters)
        
        return TriggerList(
            items=[TriggerRead.model_validate(t) for t in triggers],
            total=total,
            page=skip // limit + 1,
            page_size=limit
        )
    
    async def activate_trigger(self, trigger_id: str) -> Optional[TriggerRead]:
        """Activate a trigger"""
        trigger = await self.repository.get(trigger_id)
        if not trigger:
            return None
        
        trigger.enabled = True
        trigger.status = TriggerStatus.ACTIVE
        trigger.updated_at = datetime.now()
        
        updated_trigger = await self.repository.update(trigger_id, trigger)
        return TriggerRead.model_validate(updated_trigger)
    
    async def deactivate_trigger(self, trigger_id: str) -> Optional[TriggerRead]:
        """Deactivate a trigger"""
        trigger = await self.repository.get(trigger_id)
        if not trigger:
            return None
        
        trigger.enabled = False
        trigger.status = TriggerStatus.INACTIVE
        trigger.updated_at = datetime.now()
        
        updated_trigger = await self.repository.update(trigger_id, trigger)
        return TriggerRead.model_validate(updated_trigger)
    
    async def process_event(self, event: TriggerEvent) -> List[TriggerResult]:
        """
        Process an incoming event against all active triggers
        
        Returns a list of trigger execution results
        """
        # Get all active event-based triggers
        active_triggers = await self.repository.list_active_event_triggers()
        
        results = []
        for trigger in active_triggers:
            # Check if the trigger matches this event
            if self._does_trigger_match_event(trigger, event):
                result = await self._execute_trigger_action(trigger, event)
                results.append(result)
                
                # Update trigger metadata
                if result.success:
                    trigger.trigger_count += 1
                    trigger.last_triggered_at = datetime.now()
                else:
                    trigger.error_count += 1
                
                await self.repository.update(trigger.id, trigger)
                
        return results
    
    def _does_trigger_match_event(self, trigger: Trigger, event: TriggerEvent) -> bool:
        """Check if a trigger's rules match an event"""
        # Implementation of rule matching logic
        # This would check the trigger's rules against the event data
        # For now, a simple example implementation
        
        # Check event type matches any rule condition
        for rule in trigger.rules:
            for condition in rule.conditions:
                if condition.field == "event_type" and condition.value == event.event_type:
                    return True
                
        return False
    
    async def _execute_trigger_action(self, trigger: Trigger, event: TriggerEvent) -> TriggerResult:
        """
        Execute the action associated with a trigger
        
        Returns a TriggerResult with execution status
        """
        try:
            # Implementation of different trigger actions
            # This could call other services based on the action type
            # For now, just log the action
            
            logger.info(f"Executing trigger {trigger.id} action {trigger.action.action_type}")
            
            # In a real implementation, different actions would be handled here
            # like sending notifications, starting campaigns, etc.
            
            return TriggerResult(
                trigger_id=trigger.id,
                executed_at=datetime.now(),
                success=True,
                action_result={"status": "executed", "action_type": trigger.action.action_type}
            )
            
        except Exception as e:
            logger.error(f"Error executing trigger {trigger.id}: {str(e)}")
            return TriggerResult(
                trigger_id=trigger.id,
                executed_at=datetime.now(),
                success=False,
                error=str(e)
            )
