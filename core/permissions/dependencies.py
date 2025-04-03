from typing import Callable, List

from fastapi import Depends, HTTPException, status

from api.deps import get_current_active_user

def has_permission(permission_name: str) -> Callable:
    """
    Dependency factory that creates a dependency function to check user permissions
    
    Args:
        permission_name: Name of the permission to check
        
    Returns:
        A dependency function that can be used with FastAPI's Depends
    """
    # First define the actual dependency function
    async def check_permission():
        """Check if the current user has the required permission"""
        # For development, just pass through
        # In production, this would check the user's permissions
        return True
        
    # Important: return the function itself, not a string
    return check_permission

def has_role(role_name: str) -> Callable:
    """
    Simplified role check for development.
    """
    async def check_role(current_user: dict = Depends(get_current_active_user)):
        # For development, all checks pass
        return True
    
    return check_role

def has_any_permission(permission_names: List[str]) -> Callable:
    """
    Dependency factory that creates a dependency function to check if user has any of the permissions
    
    Args:
        permission_names: List of permission names to check
        
    Returns:
        A dependency function that can be used with FastAPI's Depends
    """
    async def check_any_permission():
        """Check if the current user has any of the required permissions"""
        # For development, just pass through
        # In production, this would check the user's permissions
        return True
        
    return check_any_permission

# Basic user dependencies - these will be updated later with proper authentication
async def get_current_user():
    """
    Dependency to get the current user based on the provided token.
    Simplified version for now.
    """
    # This would normally verify the token and return a user
    # For now, it returns a dummy user
    return {"id": "dummy_user_id", "is_active": True}

async def get_current_active_user():
    """
    Dependency to get the current active user.
    Simplified version for now.
    """
    # This would normally check if the user is active
    # For now, it returns a dummy active user
    return {"id": "dummy_user_id", "is_active": True}
