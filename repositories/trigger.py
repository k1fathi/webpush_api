from datetime import datetime
from typing import Dict, List, Optional, Any

from models.schemas.trigger import Trigger, TriggerStatus, TriggerType

class TriggerRepository:
    """Repository for trigger operations"""
    
    def __init__(self, db=None):
        self.db = db
        # For simplicity, using in-memory storage for now
        # In a real implementation, this would use a database
        self._triggers = {}
    
    async def create(self, trigger: Trigger) -> Trigger:
        """Create a new trigger"""
        if not trigger.id:
            import uuid
            trigger.id = str(uuid.uuid4())
        
        trigger.created_at = datetime.now()
        trigger.updated_at = datetime.now()
        
        self._triggers[trigger.id] = trigger
        return trigger
    
    async def get(self, trigger_id: str) -> Optional[Trigger]:
        """Get a trigger by ID"""
        return self._triggers.get(trigger_id)
    
    async def update(self, trigger_id: str, trigger: Trigger) -> Optional[Trigger]:
        """Update an existing trigger"""
        if trigger_id not in self._triggers:
            return None
        
        trigger.updated_at = datetime.now()
        self._triggers[trigger_id] = trigger
        return trigger
    
    async def delete(self, trigger_id: str) -> bool:
        """Delete a trigger"""
        if trigger_id not in self._triggers:
            return False
        
        del self._triggers[trigger_id]
        return True
    
    async def list(
        self, 
        skip: int = 0, 
        limit: int = 100,
        filters: Dict[str, Any] = None
    ) -> List[Trigger]:
        """List triggers with optional filtering"""
        triggers = list(self._triggers.values())
        
        # Apply filters if provided
        if filters:
            for k, v in filters.items():
                triggers = [t for t in triggers if getattr(t, k) == v]
        
        # Apply pagination
        return triggers[skip : skip + limit]
    
    async def count(self, filters: Dict[str, Any] = None) -> int:
        """Count triggers with optional filtering"""
        triggers = list(self._triggers.values())
        
        # Apply filters if provided
        if filters:
            for k, v in filters.items():
                triggers = [t for t in triggers if getattr(t, k) == v]
                
        return len(triggers)
    
    async def list_active_event_triggers(self) -> List[Trigger]:
        """List all active event-based triggers"""
        return [
            t for t in self._triggers.values()
            if t.enabled and t.status == TriggerStatus.ACTIVE and t.trigger_type == TriggerType.EVENT
        ]
