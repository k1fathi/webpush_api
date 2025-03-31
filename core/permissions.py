from fastapi import HTTPException, Depends
from functools import wraps
from db.models.roles import Role, Permission
from typing import List, Callable

class PermissionDenied(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=403,
            detail="You don't have permission to perform this action"
        )

ROLE_PERMISSIONS = {
    Role.END_USER: [],
    Role.MARKETER: [
        Permission.CAMPAIGN_MANAGEMENT,
    ],
    Role.ANALYST: [
        Permission.ANALYTICS_ACCESS,
    ],
    Role.TECH_ADMIN: [
        Permission.SYSTEM_CONFIGURATION,
        Permission.INTEGRATION_MANAGEMENT,
    ],
    Role.ADMIN: [
        Permission.FULL_ACCESS,
    ]
}

SWIMLANE_PERMISSIONS = {
    "End User": {
        "Interact with WebPush": [],
    },
    "Marketing Team": {
        "Define Campaign": [Permission.CAMPAIGN_MANAGEMENT],
        "Select Recipients": [Permission.CAMPAIGN_MANAGEMENT],
        "Choose Template": [Permission.CAMPAIGN_MANAGEMENT],
        "Personalize Message": [Permission.CAMPAIGN_MANAGEMENT],
        "Schedule Campaign": [Permission.CAMPAIGN_MANAGEMENT],
        "Send WebPush": [Permission.CAMPAIGN_MANAGEMENT],
    },
    "Data Analytics": {
        "Track Delivery": [Permission.ANALYTICS_ACCESS],
        "Analyze Performance": [Permission.ANALYTICS_ACCESS],
        "Optimize Campaign": [Permission.ANALYTICS_ACCESS],
    },
    "Technical Team": {
        "Set Up Webhook": [Permission.SYSTEM_CONFIGURATION],
        "Process Webhook": [Permission.SYSTEM_CONFIGURATION],
        "Real-time Data Analysis": [Permission.SYSTEM_CONFIGURATION],
        "Manage CDP Integration": [Permission.INTEGRATION_MANAGEMENT],
        "Manage CEP Integration": [Permission.INTEGRATION_MANAGEMENT],
    },
    "System Admin": {
        "Manage Users": [Permission.FULL_ACCESS],
        "Configure Permissions": [Permission.FULL_ACCESS],
        "System Settings": [Permission.FULL_ACCESS],
    }
}

# Default permissions for each role
DEFAULT_ROLE_PERMISSIONS = {
    Role.ADMIN: [
        Permission.FULL_ACCESS,
        Permission.CAMPAIGN_MANAGEMENT,
        Permission.ANALYTICS_ACCESS,
        Permission.SYSTEM_CONFIGURATION,
        Permission.INTEGRATION_MANAGEMENT
    ],
    Role.TECH_ADMIN: [
        Permission.SYSTEM_CONFIGURATION,
        Permission.INTEGRATION_MANAGEMENT
    ],
    Role.MARKETER: [
        Permission.CAMPAIGN_MANAGEMENT
    ],
    Role.ANALYST: [
        Permission.ANALYTICS_ACCESS
    ],
    Role.END_USER: []
}

def setup_default_permissions(db_session):
    """Initialize default permissions in the database"""
    # Create default permissions
    default_permissions = {
        Permission.FULL_ACCESS: "Complete access to all system features",
        Permission.CAMPAIGN_MANAGEMENT: "Manage marketing campaigns and notifications",
        Permission.ANALYTICS_ACCESS: "Access to analytics and reporting",
        Permission.SYSTEM_CONFIGURATION: "Configure system settings and integrations",
        Permission.INTEGRATION_MANAGEMENT: "Manage external system integrations"
    }
    
    for perm_name, description in default_permissions.items():
        if not db_session.query(Permission).filter_by(name=perm_name).first():
            permission = Permission(name=perm_name, description=description)
            db_session.add(permission)
    
    # Create default roles with their permissions
    for role_name, permissions in DEFAULT_ROLE_PERMISSIONS.items():
        role = db_session.query(Role).filter_by(name=role_name).first()
        if not role:
            role = Role(name=role_name)
            db_session.add(role)
            
        # Assign default permissions to role
        for perm_name in permissions:
            permission = db_session.query(Permission).filter_by(name=perm_name).first()
            if permission and permission not in role.permissions:
                role.permissions.append(permission)
    
    db_session.commit()

def assign_default_role_permissions(user, role_name, db_session):
    """Assign default permissions to a user based on their role"""
    role = db_session.query(Role).filter_by(name=role_name).first()
    if not role:
        raise ValueError(f"Role {role_name} not found")
    
    user.roles.append(role)
    db_session.commit()

def require_permissions(permissions: List[str]) -> Callable:
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            user = kwargs.get('current_user')
            if not user:
                raise HTTPException(status_code=401, detail="Not authenticated")
            
            # Check if user has ADMIN role - bypass all permission checks
            if any(role.name == Role.ADMIN for role in user.roles):
                return await func(*args, **kwargs)
                
            # For non-admin users, check specific permissions
            user_permissions = set()
            for role in user.roles:
                user_permissions.update(ROLE_PERMISSIONS.get(role.name, []))
                
            if not set(permissions).issubset(user_permissions):
                raise PermissionDenied()
                
            return await func(*args, **kwargs)
        return wrapper
    return decorator

def is_admin(user) -> bool:
    """Helper function to check if user has ADMIN role"""
    return any(role.name == Role.ADMIN for role in user.roles)

# Update permission check helper
def check_permission(user, required_permissions: List[str]) -> bool:
    """Check if user has required permissions or is admin"""
    if is_admin(user):
        return True
        
    user_permissions = set()
    for role in user.roles:
        user_permissions.update(ROLE_PERMISSIONS.get(role.name, []))
    
    return set(required_permissions).issubset(user_permissions)
