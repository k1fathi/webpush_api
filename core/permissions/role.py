from typing import Dict, List, Set

from .permission import PERMISSIONS, Permission

class Role:
    def __init__(self, name: str, description: str, permissions: List[str] = None):
        self.name = name
        self.description = description
        self.permissions = set(permissions or [])
    
    def has_permission(self, permission_name: str) -> bool:
        return permission_name in self.permissions
    
    def add_permission(self, permission_name: str) -> None:
        if permission_name in PERMISSIONS:
            self.permissions.add(permission_name)
    
    def remove_permission(self, permission_name: str) -> None:
        if permission_name in self.permissions:
            self.permissions.remove(permission_name)

# Define system roles based on the roles_permissions.md document
SYSTEM_ADMINISTRATOR = Role(
    name="system_administrator",
    description="Has complete unrestricted access to all system features and configurations.",
    permissions=list(PERMISSIONS.keys())  # All permissions
)

MARKETING_MANAGER = Role(
    name="marketing_manager",
    description="Responsible for overseeing the marketing strategy and campaign performance.",
    permissions=[
        # Campaign permissions
        "read_campaign", "create_campaign", "update_campaign", "delete_campaign", "list_campaigns", 
        "publish_campaign", "approve_campaign",
        
        # Segment permissions
        "read_segment", "create_segment", "list_segments",
        
        # Template permissions
        "read_template", "create_template", "update_template", "delete_template", "list_templates",
        
        # Analytics permissions
        "read_analytics", "export_analytics",
        
        # Limited user management
        "read_user", "list_users",
        
        # AB Test permissions
        "read_ab_test", "create_ab_test", "update_ab_test", "list_ab_tests",
        
        # CDP and CEP view access
        "read_cdp_integration", "read_cep_decision",
    ]
)

CAMPAIGN_MANAGER = Role(
    name="campaign_manager",
    description="Creates, schedules, and manages WebPush campaigns.",
    permissions=[
        # Campaign permissions
        "read_campaign", "create_campaign", "update_campaign", "delete_campaign", "list_campaigns", 
        "publish_campaign",
        
        # Segment permissions (read-only)
        "read_segment", "list_segments",
        
        # Template permissions
        "read_template", "list_templates",
        
        # Analytics permissions (limited)
        "read_analytics",
        
        # AB Test permissions
        "read_ab_test", "create_ab_test", "update_ab_test", "list_ab_tests",
        
        # Trigger permissions
        "create_trigger", "read_trigger", "update_trigger", "delete_trigger", "list_triggers",
        
        # CDP access (limited)
        "read_cdp_integration",
    ]
)

CONTENT_EDITOR = Role(
    name="content_editor",
    description="Creates and manages notification templates and content.",
    permissions=[
        # Template permissions
        "read_template", "create_template", "update_template", "delete_template", "list_templates",
        
        # Campaign permissions (limited)
        "read_campaign", "list_campaigns",
    ]
)

ANALYTICS_SPECIALIST = Role(
    name="analytics_specialist",
    description="Analyzes campaign performance and creates reports.",
    permissions=[
        # Analytics permissions
        "read_analytics", "export_analytics",
        
        # Read-only access to related data
        "read_campaign", "list_campaigns",
        "read_segment", "list_segments",
        "read_template", "list_templates",
        "read_ab_test", "list_ab_tests",
        
        # CDP access for reporting
        "read_cdp_integration",
    ]
)

SEGMENT_MANAGER = Role(
    name="segment_manager",
    description="Creates and manages user segments for targeting.",
    permissions=[
        # Segment permissions
        "read_segment", "create_segment", "update_segment", "delete_segment", "list_segments",
        
        # User permissions (limited)
        "read_user", "list_users",
        
        # Analytics permissions (limited to segments)
        "read_analytics",
        
        # CDP access for segmentation
        "read_cdp_integration",
    ]
)

INTEGRATION_SPECIALIST = Role(
    name="integration_specialist",
    description="Manages external system integrations and webhooks.",
    permissions=[
        # Webhook permissions
        "read_webhook", "create_webhook", "update_webhook", "delete_webhook", "list_webhooks",
        
        # Integration permissions
        "read_cdp_integration", "update_cdp_integration",
        "read_cep_decision", "update_cep_decision",
        
        # Notification permissions (limited)
        "read_notification", "list_notifications",
        
        # Trigger permissions (integration-related)
        "read_trigger", "list_triggers", "execute_trigger",
    ]
)

# Store all roles in a dictionary for easy lookup
ROLES = {
    "system_administrator": SYSTEM_ADMINISTRATOR,
    "marketing_manager": MARKETING_MANAGER,
    "campaign_manager": CAMPAIGN_MANAGER,
    "content_editor": CONTENT_EDITOR,
    "analytics_specialist": ANALYTICS_SPECIALIST,
    "segment_manager": SEGMENT_MANAGER,
    "integration_specialist": INTEGRATION_SPECIALIST,
}
