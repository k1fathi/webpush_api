from db.models.roles import Role, Permission
from typing import Dict, List

SWIMLANE_ACTIVITY_PERMISSIONS: Dict[str, Dict[str, List[str]]] = {
    Role.END_USER: {
        "activities": [
            "Receive WebPush",
            "Open WebPush",
            "Click WebPush"
        ],
        "permissions": []
    },
    Role.MARKETER: {
        "activities": [
            "Define Campaign",
            "Select Recipients",
            "Choose Template",
            "Personalize Message",
            "Schedule Campaign",
            "Send WebPush"
        ],
        "permissions": [
            Permission.CAMPAIGN_MANAGEMENT
        ]
    },
    Role.ANALYST: {
        "activities": [
            "Track Delivery",
            "Analyze Performance",
            "Optimize Campaign"
        ],
        "permissions": [
            Permission.ANALYTICS_ACCESS
        ]
    },
    Role.TECH_ADMIN: {
        "activities": [
            "Set Up Webhook",
            "Process Webhook",
            "Real-time Data Analysis",
            "Integrate CDP Data",
            "Integrate CEP Data"
        ],
        "permissions": [
            Permission.SYSTEM_CONFIGURATION,
            Permission.INTEGRATION_MANAGEMENT
        ]
    },
    Role.ADMIN: {
        "activities": [
            "Manage Users",
            "Configure Permissions",
            "System Settings",
            "Access All Features"
        ],
        "permissions": [
            Permission.FULL_ACCESS
        ]
    }
}

def seed_role_permissions(db_session) -> None:
    """Seed the database with default role permissions and activities"""
    
    # Create all permissions first
    permission_descriptions = {
        Permission.FULL_ACCESS: "Complete access to all system features and activities",
        Permission.CAMPAIGN_MANAGEMENT: "Create and manage marketing campaigns and notifications",
        Permission.ANALYTICS_ACCESS: "Access to analytics, reporting and performance metrics",
        Permission.SYSTEM_CONFIGURATION: "Configure system settings, webhooks and technical features",
        Permission.INTEGRATION_MANAGEMENT: "Manage CDP and CEP integrations"
    }

    for perm_name, description in permission_descriptions.items():
        if not db_session.query(Permission).filter_by(name=perm_name).first():
            permission = Permission(name=perm_name, description=description)
            db_session.add(permission)
    
    db_session.commit()

    # Create roles with their activities and permissions
    for role_name, config in SWIMLANE_ACTIVITY_PERMISSIONS.items():
        role = db_session.query(Role).filter_by(name=role_name).first()
        if not role:
            role = Role(
                name=role_name,
                description=f"Role for {role_name} with {len(config['activities'])} activities"
            )
            db_session.add(role)
            db_session.commit()

        # Assign permissions to role
        for perm_name in config['permissions']:
            permission = db_session.query(Permission).filter_by(name=perm_name).first()
            if permission and permission not in role.permissions:
                role.permissions.append(permission)
    
    db_session.commit()
