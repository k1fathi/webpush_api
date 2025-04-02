import logging
import json
from datetime import datetime
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

def audit_log(
    message: str,
    action_type: str,
    resource_type: Optional[str] = None,
    resource_id: Optional[str] = None,
    user_id: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Log an audit event
    
    Args:
        message: Description of the event
        action_type: Type of action (create, update, delete, etc.)
        resource_type: Type of resource (user, campaign, etc.)
        resource_id: ID of the resource
        user_id: ID of the user who performed the action
        metadata: Additional data about the event
        
    Returns:
        Dictionary containing the audit log entry
    """
    log_entry = {
        "message": message,
        "action": action_type,
        "timestamp": datetime.now().isoformat(),
        "metadata": metadata or {}
    }
    
    if resource_type:
        log_entry["resource_type"] = resource_type
    
    if resource_id:
        log_entry["resource_id"] = resource_id
    
    if user_id:
        log_entry["user_id"] = user_id
    
    # Log using standard logger
    logger.info(f"AUDIT: {message}", extra=log_entry)
    
    # In a real implementation, you might also:
    # 1. Store in database
    # 2. Send to external logging system
    # 3. Trigger alerts for certain events
    
    return log_entry
