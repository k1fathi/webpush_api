"""
This module helps resolve circular dependency issues between models.

When you have SQLAlchemy models referencing each other in a circular manner,
use string-based relationship references rather than direct class references.

Example:
    # Instead of this (which causes circular imports):
    from models.other import OtherModel
    related = relationship(OtherModel, back_populates="related_back")
    
    # Do this (which avoids circular imports):
    related = relationship("OtherModel", back_populates="related_back")
"""

def fix_circular_imports():
    """
    Import all models to ensure they're registered with SQLAlchemy.
    
    This function should be called before running database operations
    if you encounter circular dependency issues.
    """
    # Import all models to ensure they're registered with SQLAlchemy
    # The imports are done inside the function to avoid circular imports
    # when this module itself is imported
    
    try:
        from models.domain.user import UserModel
        from models.domain.role import RoleModel
    except ImportError as e:
        print(f"Warning: Could not import user/role models: {str(e)}")
    
    try:
        from models.domain.notification import NotificationModel
    except ImportError:
        pass
    
    try:
        from models.domain.analytics import AnalyticsModel
    except ImportError:
        pass
    
    # Add any other model imports that might be part of the circular dependency
    
    return True
