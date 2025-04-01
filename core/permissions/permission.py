from enum import Enum, auto

class ResourceType(str, Enum):
    USER = "user"
    ROLE = "role"
    SEGMENT = "segment"
    TEMPLATE = "template"
    CAMPAIGN = "campaign"
    NOTIFICATION = "notification"
    TRIGGER = "trigger"
    WEBHOOK = "webhook"
    ANALYTICS = "analytics"
    CDP_INTEGRATION = "cdp_integration"
    CEP_DECISION = "cep_decision"
    AB_TEST = "ab_test"
    SYSTEM_SETTINGS = "system_settings"

class Action(str, Enum):
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    LIST = "list"
    PUBLISH = "publish"
    APPROVE = "approve"
    EXECUTE = "execute"
    EXPORT = "export"

class Permission:
    def __init__(self, resource_type: ResourceType, action: Action):
        self.resource_type = resource_type
        self.action = action
    
    def __str__(self):
        return f"{self.action}_{self.resource_type}"

# Define all available permissions
PERMISSIONS = {
    # User permissions
    "create_user": Permission(ResourceType.USER, Action.CREATE),
    "read_user": Permission(ResourceType.USER, Action.READ),
    "update_user": Permission(ResourceType.USER, Action.UPDATE),
    "delete_user": Permission(ResourceType.USER, Action.DELETE),
    "list_users": Permission(ResourceType.USER, Action.LIST),
    
    # Role permissions
    "create_role": Permission(ResourceType.ROLE, Action.CREATE),
    "read_role": Permission(ResourceType.ROLE, Action.READ),
    "update_role": Permission(ResourceType.ROLE, Action.UPDATE),
    "delete_role": Permission(ResourceType.ROLE, Action.DELETE),
    "list_roles": Permission(ResourceType.ROLE, Action.LIST),
    
    # Segment permissions
    "create_segment": Permission(ResourceType.SEGMENT, Action.CREATE),
    "read_segment": Permission(ResourceType.SEGMENT, Action.READ),
    "update_segment": Permission(ResourceType.SEGMENT, Action.UPDATE),
    "delete_segment": Permission(ResourceType.SEGMENT, Action.DELETE),
    "list_segments": Permission(ResourceType.SEGMENT, Action.LIST),
    
    # Template permissions
    "create_template": Permission(ResourceType.TEMPLATE, Action.CREATE),
    "read_template": Permission(ResourceType.TEMPLATE, Action.READ),
    "update_template": Permission(ResourceType.TEMPLATE, Action.UPDATE),
    "delete_template": Permission(ResourceType.TEMPLATE, Action.DELETE),
    "list_templates": Permission(ResourceType.TEMPLATE, Action.LIST),
    
    # Campaign permissions
    "create_campaign": Permission(ResourceType.CAMPAIGN, Action.CREATE),
    "read_campaign": Permission(ResourceType.CAMPAIGN, Action.READ),
    "update_campaign": Permission(ResourceType.CAMPAIGN, Action.UPDATE),
    "delete_campaign": Permission(ResourceType.CAMPAIGN, Action.DELETE),
    "list_campaigns": Permission(ResourceType.CAMPAIGN, Action.LIST),
    "publish_campaign": Permission(ResourceType.CAMPAIGN, Action.PUBLISH),
    "approve_campaign": Permission(ResourceType.CAMPAIGN, Action.APPROVE),
    
    # Notification permissions
    "create_notification": Permission(ResourceType.NOTIFICATION, Action.CREATE),
    "read_notification": Permission(ResourceType.NOTIFICATION, Action.READ),
    "list_notifications": Permission(ResourceType.NOTIFICATION, Action.LIST),
    
    # Trigger permissions
    "create_trigger": Permission(ResourceType.TRIGGER, Action.CREATE),
    "read_trigger": Permission(ResourceType.TRIGGER, Action.READ),
    "update_trigger": Permission(ResourceType.TRIGGER, Action.UPDATE),
    "delete_trigger": Permission(ResourceType.TRIGGER, Action.DELETE),
    "list_triggers": Permission(ResourceType.TRIGGER, Action.LIST),
    "execute_trigger": Permission(ResourceType.TRIGGER, Action.EXECUTE),
    
    # Webhook permissions
    "create_webhook": Permission(ResourceType.WEBHOOK, Action.CREATE),
    "read_webhook": Permission(ResourceType.WEBHOOK, Action.READ),
    "update_webhook": Permission(ResourceType.WEBHOOK, Action.UPDATE),
    "delete_webhook": Permission(ResourceType.WEBHOOK, Action.DELETE),
    "list_webhooks": Permission(ResourceType.WEBHOOK, Action.LIST),
    
    # Analytics permissions
    "read_analytics": Permission(ResourceType.ANALYTICS, Action.READ),
    "export_analytics": Permission(ResourceType.ANALYTICS, Action.EXPORT),
    
    # AB Test permissions
    "create_ab_test": Permission(ResourceType.AB_TEST, Action.CREATE),
    "read_ab_test": Permission(ResourceType.AB_TEST, Action.READ),
    "update_ab_test": Permission(ResourceType.AB_TEST, Action.UPDATE),
    "delete_ab_test": Permission(ResourceType.AB_TEST, Action.DELETE),
    "list_ab_tests": Permission(ResourceType.AB_TEST, Action.LIST),
    
    # CDP Integration permissions
    "read_cdp_integration": Permission(ResourceType.CDP_INTEGRATION, Action.READ),
    "update_cdp_integration": Permission(ResourceType.CDP_INTEGRATION, Action.UPDATE),
    
    # CEP Decision permissions
    "read_cep_decision": Permission(ResourceType.CEP_DECISION, Action.READ),
    "update_cep_decision": Permission(ResourceType.CEP_DECISION, Action.UPDATE),
    
    # System Settings permissions
    "read_system_settings": Permission(ResourceType.SYSTEM_SETTINGS, Action.READ),
    "update_system_settings": Permission(ResourceType.SYSTEM_SETTINGS, Action.UPDATE),
}
