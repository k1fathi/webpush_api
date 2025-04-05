from datetime import datetime
from typing import Dict, List, Optional, Any

from models.schemas.webhook import Webhook

class WebhookRepository:
    """Repository for webhook operations"""
    
    def __init__(self, db=None):
        self.db = db
        # For simplicity, using in-memory storage for now
        # In a real implementation, this would use a database
        self._webhooks = {}
    
    async def create(self, webhook: Webhook) -> Webhook:
        """Create a new webhook"""
        self._webhooks[webhook.id] = webhook
        return webhook
    
    async def get(self, webhook_id: str) -> Optional[Webhook]:
        """Get a webhook by ID"""
        return self._webhooks.get(webhook_id)
    
    async def update(self, webhook_id: str, webhook: Webhook) -> Optional[Webhook]:
        """Update an existing webhook"""
        if webhook_id not in self._webhooks:
            return None
        
        self._webhooks[webhook_id] = webhook
        return webhook
    
    async def delete(self, webhook_id: str) -> bool:
        """Delete a webhook"""
        if webhook_id not in self._webhooks:
            return False
        
        del self._webhooks[webhook_id]
        return True
    
    async def list(
        self, 
        skip: int = 0, 
        limit: int = 100,
        filters: Dict[str, Any] = None
    ) -> List[Webhook]:
        """List webhooks with optional filtering"""
        webhooks = list(self._webhooks.values())
        
        # Apply filters if provided
        if filters:
            for k, v in filters.items():
                webhooks = [w for w in webhooks if getattr(w, k) == v]
        
        # Apply pagination
        return webhooks[skip : skip + limit]
    
    async def count(self, filters: Dict[str, Any] = None) -> int:
        """Count webhooks with optional filtering"""
        webhooks = list(self._webhooks.values())
        
        # Apply filters if provided
        if filters:
            for k, v in filters.items():
                webhooks = [w for w in webhooks if getattr(w, k) == v]
                
        return len(webhooks)
    
    async def find_by_event_type(self, event_type: str) -> List[Webhook]:
        """Find webhooks by event type"""
        return [w for w in self._webhooks.values() 
                if w.event_type == event_type and w.is_active]
