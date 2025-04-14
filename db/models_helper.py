"""
Helper module to ensure proper model loading and dependencies resolution.
This module ensures all models are imported in the correct order to prevent
circular dependency issues and foreign key reference errors.
"""

def load_all_models():
    """
    Import all models in the correct order to ensure proper table creation.
    This function should be called in alembic env.py before accessing Base.metadata.
    """
    # Import Base first
    from db.base_class import Base
    
    # Import independent models first (no foreign key dependencies)
    from models.domain.role import RoleModel
    from models.domain.user import UserModel
    
    # Import models with dependencies
    # Make sure to import the 'notifications' table before 'analytics'
    try:
        from models.domain.notification import NotificationModel
    except ImportError as e:
        print(f"Warning: Could not import notification model: {str(e)}")
        # If NotificationModel doesn't exist, we need to create it
        print("Creating NotificationModel placeholder to satisfy foreign key relationships")
        
        # Create a placeholder model for notifications if it doesn't exist
        from sqlalchemy import Column, String, DateTime, Boolean, Text, Integer
        from sqlalchemy.dialects.postgresql import UUID
        import uuid
        
        class NotificationModel(Base):
            __tablename__ = "notifications"
            
            id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
            title = Column(String(255), nullable=False)
            body = Column(Text, nullable=True)
            status = Column(String(50), nullable=False, default="pending")
            created_at = Column(DateTime, nullable=False)
            updated_at = Column(DateTime, nullable=True)
            is_read = Column(Boolean, default=False)
            
            def __repr__(self):
                return f"<Notification {self.title}>"
    
    # Now import models that depend on notifications
    try:
        from models.domain.analytics import AnalyticsModel
    except ImportError as e:
        print(f"Warning: Could not import analytics model: {str(e)}")
    
    # Import any other models that might have dependencies
    # ...
    
    return True
