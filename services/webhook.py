import logging
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any

try:
    import httpx
except ImportError:
    httpx = None
    logging.warning("httpx module not found. Webhook functionality will be limited.")

from models.schemas.webhook import (
    Webhook, WebhookCreate, WebhookRead, WebhookUpdate, WebhookList, WebhookEventType
)
from repositories.webhook import WebhookRepository
from utils.audit import audit_log

logger = logging.getLogger(__name__)

class WebhookService:
    """Service for managing webhooks"""
    
    def __init__(self, repository: WebhookRepository):
        self.repository = repository
        self.http_client = httpx.AsyncClient() if httpx else None
        
    async def create_webhook(self, webhook_create: WebhookCreate) -> WebhookRead:
        """Create a new webhook"""
        # Generate secret key if not provided
        if not webhook_create.secret_key:
            import secrets
            secret_key = secrets.token_hex(16)
        else:
            secret_key = webhook_create.secret_key
        
        # Create webhook object
        webhook = Webhook(
            id=str(uuid.uuid4()),
            name=webhook_create.name,
            endpoint_url=webhook_create.endpoint_url,
            event_type=webhook_create.event_type,
            secret_key=secret_key,
            is_active=True,
            created_at=datetime.now()
        )
        
        # Save to database
        created_webhook = await self.repository.create(webhook)
        
        audit_log(f"Created webhook {webhook.id} for event type {webhook.event_type}")
        
        return WebhookRead.model_validate(created_webhook)
    
    async def get_webhook(self, webhook_id: str) -> Optional[WebhookRead]:
        """Get a webhook by ID"""
        webhook = await self.repository.get(webhook_id)
        if not webhook:
            return None
        return WebhookRead.model_validate(webhook)
    
    async def update_webhook(self, webhook_id: str, webhook_update: WebhookUpdate) -> Optional[WebhookRead]:
        """Update a webhook"""
        # First get existing webhook
        webhook = await self.repository.get(webhook_id)
        if not webhook:
            return None
        
        # Update fields
        update_data = webhook_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(webhook, key, value)
        
        # Save to database
        updated_webhook = await self.repository.update(webhook_id, webhook)
        
        audit_log(f"Updated webhook {webhook_id}")
        
        return WebhookRead.model_validate(updated_webhook)
    
    async def delete_webhook(self, webhook_id: str) -> bool:
        """Delete a webhook"""
        result = await self.repository.delete(webhook_id)
        if result:
            audit_log(f"Deleted webhook {webhook_id}")
        return result
    
    async def list_webhooks(
        self, 
        skip: int = 0, 
        limit: int = 100,
        event_type: Optional[WebhookEventType] = None,
        is_active: Optional[bool] = None
    ) -> WebhookList:
        """List all webhooks with filtering options"""
        filters = {}
        if event_type:
            filters["event_type"] = event_type
        if is_active is not None:
            filters["is_active"] = is_active
            
        webhooks = await self.repository.list(
            skip=skip,
            limit=limit,
            filters=filters
        )
        total = await self.repository.count(filters)
        
        return WebhookList(
            items=[WebhookRead.model_validate(t) for t in webhooks],
            total=total,
            page=skip // limit + 1 if limit > 0 else 1,
            page_size=limit
        )
    
    async def activate_webhook(self, webhook_id: str) -> Optional[WebhookRead]:
        """Activate a webhook"""
        webhook = await self.repository.get(webhook_id)
        if not webhook:
            return None
        
        webhook.is_active = True
        
        updated_webhook = await self.repository.update(webhook_id, webhook)
        
        audit_log(f"Activated webhook {webhook_id}")
        
        return WebhookRead.model_validate(updated_webhook)
    
    async def deactivate_webhook(self, webhook_id: str) -> Optional[WebhookRead]:
        """Deactivate a webhook"""
        webhook = await self.repository.get(webhook_id)
        if not webhook:
            return None
        
        webhook.is_active = False
        
        updated_webhook = await self.repository.update(webhook_id, webhook)
        
        audit_log(f"Deactivated webhook {webhook_id}")
        
        return WebhookRead.model_validate(updated_webhook)
    
    async def trigger_webhook(self, webhook_id: str, payload: Dict[str, Any]) -> bool:
        """
        Trigger a webhook by sending the specified payload
        
        Returns True if successful, False otherwise
        """
        webhook = await self.repository.get(webhook_id)
        if not webhook or not webhook.is_active:
            logger.warning(f"Cannot trigger webhook {webhook_id}: not found or inactive")
            return False
            
        if not self.http_client:
            logger.error("Cannot trigger webhook: httpx module not installed")
            return False
            
        try:
            # Add signature headers
            headers = {
                "Content-Type": "application/json",
                "X-Webhook-Signature": self._generate_signature(webhook.secret_key, payload),
                "X-Webhook-Event": webhook.event_type,
                "X-Webhook-ID": webhook.id
            }
            
            # Send request
            response = await self.http_client.post(
                str(webhook.endpoint_url),
                json=payload,
                headers=headers,
                timeout=10.0
            )
            
            success = 200 <= response.status_code < 300
            
            # Update last triggered timestamp
            if success:
                webhook.last_triggered_at = datetime.now()
                await self.repository.update(webhook.id, webhook)
                
            return success
            
        except Exception as e:
            logger.error(f"Failed to trigger webhook {webhook_id}: {str(e)}")
            return False
            
    async def test_webhook(self, webhook_id: str) -> Tuple[bool, str]:
        """
        Send a test payload to the webhook endpoint
        
        Returns a tuple of (success, message)
        """
        webhook = await self.repository.get(webhook_id)
        if not webhook:
            return False, "Webhook not found"
            
        # Create test payload
        test_payload = {
            "event": "webhook_test",
            "timestamp": datetime.now().isoformat(),
            "webhook_id": webhook.id,
            "message": "This is a test webhook notification"
        }
        
        success = await self.trigger_webhook(webhook_id, test_payload)
        
        if success:
            return True, "Test webhook sent successfully"
        else:
            return False, "Failed to send test webhook"
    
    def _generate_signature(self, secret: str, payload: Dict[str, Any]) -> str:
        """Generate a signature for the webhook payload"""
        import hmac
        import hashlib
        import json
        
        # Convert payload to JSON string
        payload_str = json.dumps(payload, sort_keys=True)
        
        # Generate HMAC signature
        signature = hmac.new(
            secret.encode(),
            payload_str.encode(),
            hashlib.sha256
        ).hexdigest()
        
        return signature
        
    async def close(self):
        """Close HTTP connection"""
        if self.http_client:
            await self.http_client.aclose()
