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

# Define permissions used in the application
# This helps avoid typos and inconsistencies when using permission strings

# User permissions
USER_CREATE = "create_user"
USER_READ = "read_user" 
USER_UPDATE = "update_user"
USER_DELETE = "delete_user"
USER_LIST = "list_users"
USER_ACTIVATE = "activate_user"
USER_DEACTIVATE = "deactivate_user"

# Campaign permissions
CAMPAIGN_CREATE = "create_campaign"
CAMPAIGN_READ = "read_campaign"
CAMPAIGN_UPDATE = "update_campaign"
CAMPAIGN_DELETE = "delete_campaign"
CAMPAIGN_LIST = "list_campaigns"
CAMPAIGN_PUBLISH = "publish_campaign"
CAMPAIGN_APPROVE = "approve_campaign"

# Template permissions
TEMPLATE_CREATE = "create_template"
TEMPLATE_READ = "read_template"
TEMPLATE_UPDATE = "update_template"
TEMPLATE_DELETE = "delete_template"
TEMPLATE_LIST = "list_templates"
TEMPLATE_APPROVE = "approve_template"
TEMPLATE_SUBMIT = "submit_template"
TEMPLATE_ARCHIVE = "archive_template"

# Segment permissions
SEGMENT_CREATE = "create_segment"
SEGMENT_READ = "read_segment"
SEGMENT_UPDATE = "update_segment"
SEGMENT_DELETE = "delete_segment"
SEGMENT_LIST = "list_segments"
SEGMENT_EVALUATE = "evaluate_segment"
SEGMENT_EXECUTE = "execute_segment"

# Notification permissions
NOTIFICATION_CREATE = "create_notification"
NOTIFICATION_READ = "read_notification"
NOTIFICATION_SEND = "send_notification"

# Analytics permissions
READ_ANALYTICS = "read_analytics"
CREATE_ANALYTICS = "create_analytics"
EXPORT_ANALYTICS = "export_analytics"

# AB Test permissions
AB_TEST_CREATE = "create_ab_test"
AB_TEST_READ = "read_ab_test"
AB_TEST_UPDATE = "update_ab_test"
AB_TEST_LIST = "list_ab_tests"

# CEP permissions
CEP_READ = "read_cep_decision"
CEP_UPDATE = "update_cep_decision"
CEP_CREATE = "create_cep_decision"

# Group all permissions for reference
PERMISSIONS = {
    "user": [USER_CREATE, USER_READ, USER_UPDATE, USER_DELETE, USER_LIST, USER_ACTIVATE, USER_DEACTIVATE],
    "campaign": [CAMPAIGN_CREATE, CAMPAIGN_READ, CAMPAIGN_UPDATE, CAMPAIGN_DELETE, CAMPAIGN_LIST, CAMPAIGN_PUBLISH, CAMPAIGN_APPROVE],
    "template": [TEMPLATE_CREATE, TEMPLATE_READ, TEMPLATE_UPDATE, TEMPLATE_DELETE, TEMPLATE_LIST, TEMPLATE_APPROVE, TEMPLATE_SUBMIT, TEMPLATE_ARCHIVE],
    "segment": [SEGMENT_CREATE, SEGMENT_READ, SEGMENT_UPDATE, SEGMENT_DELETE, SEGMENT_LIST, SEGMENT_EVALUATE, SEGMENT_EXECUTE],
    "notification": [NOTIFICATION_CREATE, NOTIFICATION_READ, NOTIFICATION_SEND],
    "analytics": [READ_ANALYTICS, CREATE_ANALYTICS, EXPORT_ANALYTICS],
    "ab_test": [AB_TEST_CREATE, AB_TEST_READ, AB_TEST_UPDATE, AB_TEST_LIST],
    "cep": [CEP_READ, CEP_UPDATE, CEP_CREATE]
}
