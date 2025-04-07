"""
Domain models for SQLAlchemy ORM
"""

# Import models to ensure they are registered with the ORM before relationships are accessed
from models.domain.user import UserModel
from models.domain.role import RoleModel
from models.domain.notification import NotificationModel
from models.domain.user_role import UserRoleModel
