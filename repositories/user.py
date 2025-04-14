import datetime
import uuid
from typing import Dict, List, Optional, Any

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from db.session import get_async_session_context
from models.domain.user import UserModel
from models.domain.user_role import UserRoleModel
from models.domain.role import RoleModel
from models.schemas.user import User, UserStatus
from repositories.base import BaseRepository
from passlib.context import CryptContext

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserRepository(BaseRepository):
    """Repository for user operations"""
    
    async def create(self, user: User) -> User:
        """Create a new user"""
        async with get_async_session_context() as session:
            db_user = UserModel(
                id=str(uuid.uuid4()) if not user.id else user.id,
                email=user.email,
                username=user.username,
                full_name=user.full_name,
                status=user.status,
                is_active=user.is_active,
                is_superuser=user.is_superuser,
                notification_enabled=user.notification_enabled,
                webpush_enabled=user.webpush_enabled,
                email_notification_enabled=user.email_notification_enabled,
                quiet_hours_start=user.quiet_hours_start,
                quiet_hours_end=user.quiet_hours_end,
                subscription_info=user.subscription_info,
                devices=user.devices,
                timezone=user.timezone,
                language=user.language,
                custom_attributes=user.custom_attributes
            )
            session.add(db_user)
            await session.commit()
            await session.refresh(db_user)
            return User.from_orm(db_user)

    async def create_with_password(self, user: User, hashed_password: str) -> User:
        """Create a new user with a hashed password
        
        Args:
            user: User data
            hashed_password: Pre-hashed password
            
        Returns:
            User: The created user
        """
        async with get_async_session_context() as session:
            db_user = UserModel(
                id=uuid.UUID(user.id) if isinstance(user.id, str) else user.id,
                email=user.email,
                username=user.username,
                hashed_password=hashed_password,
                full_name=user.full_name,
                status=UserStatus.ACTIVE if user.is_superuser else UserStatus.PENDING,
                is_active=user.is_active,
                is_superuser=user.is_superuser,
                notification_enabled=user.notification_enabled,
                webpush_enabled=user.webpush_enabled,
                email_notification_enabled=user.email_notification_enabled,
                timezone=user.timezone,
                language=user.language,
                subscription_info=user.subscription_info if hasattr(user, "subscription_info") else {},
                devices=user.devices if hasattr(user, "devices") else [],
                custom_attributes=user.custom_attributes if hasattr(user, "custom_attributes") else {},
                created_at=datetime.datetime.utcnow(),
                updated_at=datetime.datetime.utcnow()
            )
            
            session.add(db_user)
            await session.commit()
            await session.refresh(db_user)
            
            # Convert back to schema model
            result = User(
                id=str(db_user.id),
                email=db_user.email,
                username=db_user.username,
                full_name=db_user.full_name,
                status=db_user.status,
                is_active=db_user.is_active,
                is_superuser=db_user.is_superuser,
                notification_enabled=db_user.notification_enabled,
                webpush_enabled=db_user.webpush_enabled,
                email_notification_enabled=db_user.email_notification_enabled,
                timezone=db_user.timezone,
                language=db_user.language,
                created_at=db_user.created_at,
                updated_at=db_user.updated_at
            )
            
            return result

    async def update_last_login(self, user_id: str) -> bool:
        """Update user's last login timestamp"""
        async with get_async_session_context() as session:
            result = await session.execute(
                select(UserModel).where(UserModel.id == user_id)
            )
            db_user = result.scalars().first()
            if db_user:
                db_user.last_login = datetime.now()
                await session.commit()
                return True
            return False

    async def update_last_seen(self, user_id: str) -> bool:
        """Update user's last seen timestamp"""
        async with get_async_session_context() as session:
            result = await session.execute(
                select(UserModel).where(UserModel.id == user_id)
            )
            db_user = result.scalars().first()
            if db_user:
                db_user.last_seen = datetime.now()
                await session.commit()
                return True
            return False

    async def add_device(self, user_id: str, device_data: Dict) -> bool:
        """Add a new device for a user"""
        async with get_async_session_context() as session:
            result = await session.execute(
                select(UserModel).where(UserModel.id == user_id)
            )
            db_user = result.scalars().first()
            if not db_user:
                return False

            devices = db_user.devices or []
            devices.append({
                **device_data,
                "created_at": datetime.now().isoformat(),
                "last_used": datetime.now().isoformat()
            })
            db_user.devices = devices
            
            await session.commit()
            return True

    async def get_notification_settings(self, user_id: str) -> Optional[Dict]:
        """Get user's notification settings"""
        async with get_async_session_context() as session:
            result = await session.execute(
                select(UserModel).where(UserModel.id == user_id)
            )
            db_user = result.scalars().first()
            if not db_user:
                return None
                
            return {
                "notification_enabled": db_user.notification_enabled,
                "webpush_enabled": db_user.webpush_enabled,
                "email_notification_enabled": db_user.email_notification_enabled,
                "quiet_hours_start": db_user.quiet_hours_start,
                "quiet_hours_end": db_user.quiet_hours_end
            }
    
    async def execute_raw_query(self, query: str, params: Dict[str, Any]) -> List[UserModel]:
        """
        Execute a raw SQL query to filter users
        
        Args:
            query: SQL query string
            params: Query parameters
            
        Returns:
            List of matching user models
        """
        async with get_async_session_context() as session:
            # Convert string query to SQLAlchemy text object
            sql = text(query)
            
            # Execute the query with parameters
            result = await session.execute(sql, params)
            
            # Extract user IDs from result
            user_ids = [row[0] for row in result]
            
            if not user_ids:
                return []
                
            # Fetch complete user records for these IDs
            users_query = select(UserModel).where(UserModel.id.in_(user_ids))
            users_result = await session.execute(users_query)
            return list(users_result.scalars().all())

    async def get_user_roles(self, user_id: str) -> List[str]:
        """Get all role IDs for a user"""
        async with get_async_session_context() as session:
            query = select(UserRoleModel.role_id).where(
                UserRoleModel.user_id == user_id
            )
            result = await session.execute(query)
            return [str(row[0]) for row in result.all()]

    async def get_user_role_names(self, user_id: str) -> List[str]:
        """Get all role names for a user"""
        async with get_async_session_context() as session:
            query = select(RoleModel.name).join(
                UserRoleModel,
                UserRoleModel.role_id == RoleModel.id
            ).where(
                UserRoleModel.user_id == user_id
            )
            result = await session.execute(query)
            return [row[0] for row in result.all()]

    async def get_by_customer_id(self, customer_id: str) -> Optional[UserModel]:
        """Get a user by customer ID"""
        query = select(UserModel).where(UserModel.custom_attributes["customer_id"].astext == customer_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
        
    async def get_users_by_customer_id(self, customer_id: str) -> List[UserModel]:
        """Get all users associated with a customer ID"""
        query = select(UserModel).where(UserModel.custom_attributes["customer_id"].astext == customer_id)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_by_email(self, email: str) -> Optional[UserModel]:
        """Get a user by email address"""
        async with get_async_session_context() as session:
            query = select(UserModel).where(UserModel.email == email)
            result = await session.execute(query)
            return result.scalar_one_or_none()

    async def get_by_username(self, username: str) -> Optional[UserModel]:
        """Get a user by username
        
        Args:
            username: The username to search for
            
        Returns:
            Optional[UserModel]: The user if found
        """
        async with get_async_session_context() as session:
            query = select(UserModel).where(UserModel.username == username)
            result = await session.execute(query)
            return result.scalar_one_or_none()

    async def get_password_hash(self, user_id: str) -> Optional[str]:
        """Get the hashed password for a user
        
        Args:
            user_id: The user ID
            
        Returns:
            Optional[str]: The hashed password if found
        """
        async with get_async_session_context() as session:
            query = select(UserModel.hashed_password).where(UserModel.id == user_id)
            result = await session.execute(query)
            row = result.one_or_none()
            return row[0] if row else None

    async def update(self, user_id: str, user: User) -> User:
        """Update an existing user
        
        Args:
            user_id: The user ID
            user: Updated user data
            
        Returns:
            User: The updated user
        """
        async with get_async_session_context() as session:
            query = select(UserModel).where(UserModel.id == user_id)
            result = await session.execute(query)
            db_user = result.scalar_one_or_none()
            
            if not db_user:
                raise ValueError(f"User with ID {user_id} not found")
                
            # Update fields
            if hasattr(user, "email"):
                db_user.email = user.email
            if hasattr(user, "username"):
                db_user.username = user.username
            if hasattr(user, "full_name"):
                db_user.full_name = user.full_name
            if hasattr(user, "status"):
                db_user.status = user.status
            if hasattr(user, "is_active"):
                db_user.is_active = user.is_active
            if hasattr(user, "is_superuser"):
                db_user.is_superuser = user.is_superuser
            if hasattr(user, "notification_enabled"):
                db_user.notification_enabled = user.notification_enabled
            if hasattr(user, "webpush_enabled"):
                db_user.webpush_enabled = user.webpush_enabled
            if hasattr(user, "email_notification_enabled"):
                db_user.email_notification_enabled = user.email_notification_enabled
            if hasattr(user, "quiet_hours_start"):
                db_user.quiet_hours_start = user.quiet_hours_start
            if hasattr(user, "quiet_hours_end"):
                db_user.quiet_hours_end = user.quiet_hours_end
            if hasattr(user, "timezone"):
                db_user.timezone = user.timezone
            if hasattr(user, "language"):
                db_user.language = user.language
                
            db_user.updated_at = datetime.datetime.utcnow()
            
            await session.commit()
            await session.refresh(db_user)
            
            # Convert back to schema model
            result = User(
                id=str(db_user.id),
                email=db_user.email,
                username=db_user.username,
                full_name=db_user.full_name,
                status=db_user.status,
                is_active=db_user.is_active,
                is_superuser=db_user.is_superuser,
                notification_enabled=db_user.notification_enabled,
                webpush_enabled=db_user.webpush_enabled,
                email_notification_enabled=db_user.email_notification_enabled,
                timezone=db_user.timezone,
                language=db_user.language,
                created_at=db_user.created_at,
                updated_at=db_user.updated_at
            )
            
            return result

    async def update_with_password(self, user_id: str, user: User, hashed_password: str) -> User:
        """Update a user with a new password
        
        Args:
            user_id: The user ID
            user: Updated user data
            hashed_password: New hashed password
            
        Returns:
            User: The updated user
        """
        async with get_async_session_context() as session:
            query = select(UserModel).where(UserModel.id == user_id)
            result = await session.execute(query)
            db_user = result.scalar_one_or_none()
            
            if not db_user:
                raise ValueError(f"User with ID {user_id} not found")
                
            # Update fields
            if hasattr(user, "email"):
                db_user.email = user.email
            if hasattr(user, "username"):
                db_user.username = user.username
            if hasattr(user, "full_name"):
                db_user.full_name = user.full_name
            if hasattr(user, "status"):
                db_user.status = user.status
            if hasattr(user, "is_active"):
                db_user.is_active = user.is_active
            if hasattr(user, "is_superuser"):
                db_user.is_superuser = user.is_superuser
            if hasattr(user, "notification_enabled"):
                db_user.notification_enabled = user.notification_enabled
            if hasattr(user, "webpush_enabled"):
                db_user.webpush_enabled = user.webpush_enabled
            if hasattr(user, "email_notification_enabled"):
                db_user.email_notification_enabled = user.email_notification_enabled
            if hasattr(user, "quiet_hours_start"):
                db_user.quiet_hours_start = user.quiet_hours_start
            if hasattr(user, "quiet_hours_end"):
                db_user.quiet_hours_end = user.quiet_hours_end
            if hasattr(user, "timezone"):
                db_user.timezone = user.timezone
            if hasattr(user, "language"):
                db_user.language = user.language
                
            # Update password
            db_user.hashed_password = hashed_password
            db_user.updated_at = datetime.datetime.utcnow()
            
            await session.commit()
            await session.refresh(db_user)
            
            # Convert back to schema model
            result = User(
                id=str(db_user.id),
                email=db_user.email,
                username=db_user.username,
                full_name=db_user.full_name,
                status=db_user.status,
                is_active=db_user.is_active,
                is_superuser=db_user.is_superuser,
                notification_enabled=db_user.notification_enabled,
                webpush_enabled=db_user.webpush_enabled,
                email_notification_enabled=db_user.email_notification_enabled,
                timezone=db_user.timezone,
                language=db_user.language,
                created_at=db_user.created_at,
                updated_at=db_user.updated_at
            )
            
            return result

    async def ensure_admin_exists(self) -> Optional[UserModel]:
        """
        Check if an admin user exists and create one if it doesn't
        
        Returns:
            Optional[UserModel]: The admin user that was created or found
        """
        async with get_async_session_context() as session:
            # Check if admin user already exists
            query = select(UserModel).where(
                (UserModel.username == "admin") | 
                (UserModel.email == "admin@example.com")
            )
            result = await session.execute(query)
            admin_user = result.scalar_one_or_none()
            
            if admin_user:
                return admin_user
            
            # Create admin user if it doesn't exist
            hashed_password = pwd_context.hash("admin123")
            admin_user = UserModel(
                id=uuid.uuid4(),
                email="admin@example.com",
                username="admin",
                hashed_password=hashed_password,
                full_name="Admin User",
                status=UserStatus.ACTIVE,
                is_active=True,
                is_superuser=True,
                notification_enabled=True,
                webpush_enabled=True,
                email_notification_enabled=True,
                timezone="UTC",
                language="en",
                custom_attributes={},
                created_at=datetime.datetime.utcnow(),
                updated_at=datetime.datetime.utcnow()
            )
            
            session.add(admin_user)
            await session.commit()
            await session.refresh(admin_user)
            
            return admin_user
