from datetime import datetime
from typing import Dict, List, Optional, Any

from models.schemas.notification import Notification, DeliveryStatus

class NotificationDeliveryRepository:
    """Repository for notification delivery operations"""
    
    def __init__(self, db=None):
        self.db = db
        # For simplicity, using in-memory storage for now
        # In a real implementation, this would use a database
        self._delivery_records = {}
    
    async def create_delivery_record(self, notification_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new delivery record for a notification"""
        record = {
            "notification_id": notification_id,
            "delivery_attempts": 0,
            "last_attempt": None,
            "delivered": False,
            "delivered_at": None,
            "device_info": data.get("device_info", {}),
            "error": None,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
        
        self._delivery_records[notification_id] = record
        return record
    
    async def get_delivery_record(self, notification_id: str) -> Optional[Dict[str, Any]]:
        """Get delivery record for a notification"""
        return self._delivery_records.get(notification_id)
    
    async def update_delivery_record(self, notification_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update delivery record for a notification"""
        record = self._delivery_records.get(notification_id)
        if not record:
            return None
            
        # Update the record with new data
        record.update(data)
        record["updated_at"] = datetime.now()
        
        return record
    
    async def record_delivery_attempt(self, notification_id: str, success: bool, error: Optional[str] = None) -> bool:
        """Record a delivery attempt for a notification"""
        record = self._delivery_records.get(notification_id)
        if not record:
            # Create a new record if one doesn't exist
            record = await self.create_delivery_record(notification_id, {})
        
        # Update attempt count and timestamp
        record["delivery_attempts"] += 1
        record["last_attempt"] = datetime.now()
        
        if success:
            record["delivered"] = True
            record["delivered_at"] = datetime.now()
            record["error"] = None
        else:
            record["error"] = error
            
        return success
    
    async def get_delivery_stats(self, filters: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get delivery statistics"""
        records = list(self._delivery_records.values())
        
        # Apply filters if provided
        if filters:
            for k, v in filters.items():
                records = [r for r in records if r.get(k) == v]
        
        total = len(records)
        delivered = len([r for r in records if r["delivered"]])
        
        return {
            "total": total,
            "delivered": delivered,
            "delivery_rate": (delivered / total * 100) if total > 0 else 0,
            "average_attempts": sum(r["delivery_attempts"] for r in records) / total if total > 0 else 0
        }
    
    async def list_failed_deliveries(self, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """List notifications with failed deliveries"""
        failed = [r for r in self._delivery_records.values() 
                 if r["delivery_attempts"] > 0 and not r["delivered"]]
        
        # Apply pagination
        return failed[skip : skip + limit]
