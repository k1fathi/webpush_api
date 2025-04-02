import logging
from datetime import datetime
from typing import Optional, Dict, Any, Union

logger = logging.getLogger("audit")

def audit_log(
    message: str,
    user_id: Optional[str] = None,
    action_type: Optional[str] = None,
    resource_type: Optional[str] = None,
    resource_id: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> None:
    """
    Log an audit event
    
    Args:
        message: Description of what happened
        user_id: ID of user who performed the action
        action_type: Type of action (create, update, delete, etc.)
        resource_type: Type of resource affected (segment, campaign, etc.)
        resource_id: ID of resource affected
        metadata: Additional information about the action
    """
    log_data = {
        "timestamp": datetime.now().isoformat(),
        "message": message,
        "user_id": user_id,
        "action_type": action_type,
        "resource_type": resource_type,
        "resource_id": resource_id
    }
    
    if metadata:
        log_data["metadata"] = metadata
        
    # Format for human-readable logs
    human_readable = f"{log_data['timestamp']} - {message}"
    if user_id:
        human_readable += f" (User: {user_id})"
    if resource_type and resource_id:
        human_readable += f" - {resource_type}/{resource_id}"
        
    logger.info(human_readable, extra={"audit_data": log_data})
    
    # In a real implementation, we might also:
    # - Store in database
    # - Send to external audit system
    # - Generate compliance reports
