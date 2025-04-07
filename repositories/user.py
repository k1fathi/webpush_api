import datetime
import uuid
from typing import Dict, List, Optional, Any

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from db.session import get_session
from models.domain.user import UserModel
from models.domain.user_role import UserRoleModel
from models.domain.role import RoleModel
from models.schemas.user import User
from repositories.base import BaseRepository

class UserRepository(BaseRepository):
    """Repository for user operations"""
    
    async def create(self, user: User) -> User:
        """Create a new user"""
        async with get_session() as session:
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

    async def update_last_login(self, user_id: str) -> bool:
        """Update user's last login timestamp"""
        async with get_session() as session:
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
        async with get_session() as session:
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
        async with get_session() as session:
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
        async with get_session() as session:
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
        async with get_session() as session:
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
        async with get_session() as session:
            query = select(UserRoleModel.role_id).where(
                UserRoleModel.user_id == user_id
            )
            result = await session.execute(query)
            return [str(row[0]) for row in result.all()]

    async def get_user_role_names(self, user_id: str) -> List[str]:
        """Get all role names for a user"""
        async with get_session() as session:
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
