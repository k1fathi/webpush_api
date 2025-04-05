import logging
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple

from passlib.context import CryptContext
from jose import jwt

from core.config import settings
from models.schemas.user import User, UserStatus
from models.schemas.user import UserCreate, UserUpdate, UserDevice
from repositories.user import UserRepository
from utils.audit import audit_log

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

logger = logging.getLogger(__name__)

class UserService:
    """Service for user management"""
    
    def __init__(self):
        self.user_repo = UserRepository()
    
    def _hash_password(self, password: str) -> str:
        """Hash a password using bcrypt"""
        return pwd_context.hash(password)
    
    def _verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against a hash"""
        return pwd_context.verify(plain_password, hashed_password)
    
    async def create_user(self, user_data: UserCreate) -> User:
        """
        Create a new user
        
        Args:
            user_data: User creation data
            
        Returns:
            User: The created user
        """
        # Check if user with this email already exists
        existing_user = await self.user_repo.get_by_email(user_data.email)
        if existing_user:
            raise ValueError(f"User with email {user_data.email} already exists")
        
        # Check if username is already taken
        existing_user = await self.user_repo.get_by_username(user_data.username)
        if existing_user:
            raise ValueError(f"Username {user_data.username} is already taken")
        
        # Hash the password
        hashed_password = self._hash_password(user_data.password)
        
        # Create user object
        user = User(
            id=str(uuid.uuid4()),
            email=user_data.email,
            username=user_data.username,
            full_name=user_data.full_name,
            status=UserStatus.PENDING,
            is_active=True,
            notification_enabled=user_data.notification_enabled,
            webpush_enabled=user_data.webpush_enabled,
            email_notification_enabled=user_data.email_notification_enabled,
            timezone=user_data.timezone,
            language=user_data.language,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        # Create the user with hashed password
        created_user = await self.user_repo.create_with_password(user, hashed_password)
        
        # Audit log
        audit_log(
            message=f"Created user {created_user.username}",
            resource_type="user",
            resource_id=created_user.id,
            action_type="create_user"
        )
        
        return created_user
    
    async def update_user(self, user_id: str, user_data: UserUpdate) -> User:
        """
        Update an existing user
        
        Args:
            user_id: The user ID
            user_data: Updated user data
            
        Returns:
            User: The updated user
        """
        # Get existing user
        user = await self.user_repo.get(user_id)
        if not user:
            raise ValueError(f"User with ID {user_id} not found")
        
        # Check email uniqueness if changing
        if user_data.email and user_data.email != user.email:
            existing_user = await self.user_repo.get_by_email(user_data.email)
            if existing_user:
                raise ValueError(f"Email {user_data.email} is already in use")
        
        # Check username uniqueness if changing
        if user_data.username and user_data.username != user.username:
            existing_user = await self.user_repo.get_by_username(user_data.username)
            if existing_user:
                raise ValueError(f"Username {user_data.username} is already taken")
        
        # Update fields
        update_data = user_data.dict(exclude_unset=True)
        
        # Handle password separately
        password = update_data.pop("password", None)
        
        # Update user fields
        for key, value in update_data.items():
            setattr(user, key, value)
        
        user.updated_at = datetime.now()
        
        # Save user updates
        if password:
            # Hash and update password
            hashed_password = self._hash_password(password)
            updated_user = await self.user_repo.update_with_password(user_id, user, hashed_password)
        else:
            # Update without changing password
            updated_user = await self.user_repo.update(user_id, user)
        
        # Audit log
        audit_log(
            message=f"Updated user {user.username}",
            resource_type="user",
            resource_id=user_id,
            action_type="update_user"
        )
        
        return updated_user
    
    async def delete_user(self, user_id: str) -> bool:
        """
        Delete a user
        
        Args:
            user_id: The user ID
            
        Returns:
            bool: True if deleted, False if not found
        """
        # Check if user exists
        user = await self.user_repo.get(user_id)
        if not user:
            return False
        
        # Delete the user
        result = await self.user_repo.delete(user_id)
        
        if result:
            # Audit log
            audit_log(
                message=f"Deleted user {user.username}",
                resource_type="user",
                resource_id=user_id,
                action_type="delete_user"
            )
        
        return result
    
    async def get_user(self, user_id: str) -> Optional[User]:
        """
        Get a user by ID
        
        Args:
            user_id: The user ID
            
        Returns:
            Optional[User]: The user if found
        """
        return await self.user_repo.get(user_id)
    
    async def get_user_by_email(self, email: str) -> Optional[User]:
        """
        Get a user by email
        
        Args:
            email: The user's email
            
        Returns:
            Optional[User]: The user if found
        """
        return await self.user_repo.get_by_email(email)
    
    async def get_all_users(
        self, 
        skip: int = 0, 
        limit: int = 100, 
        status: Optional[UserStatus] = None
    ) -> Tuple[List[User], int]:
        """
        Get all users with pagination
        
        Args:
            skip: Number of items to skip
            limit: Maximum number of items to return
            status: Filter by user status
            
        Returns:
            Tuple[List[User], int]: List of users and total count
        """
        users = await self.user_repo.get_all(skip, limit, status)
        total = await self.user_repo.count()
        return users, total
    
    async def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """
        Authenticate a user by email and password
        
        Args:
            email: User's email
            password: User's password
            
        Returns:
            Optional[User]: The authenticated user if successful
        """
        # Get user by email
        user = await self.user_repo.get_by_email(email)
        if not user:
            return None
        
        # Get password hash
        password_hash = await self.user_repo.get_password_hash(user.id)
        if not password_hash:
            return None
        
        # Verify password
        if not self._verify_password(password, password_hash):
            return None
        
        # Update last login time
        await self.user_repo.update_last_login(user.id)
        
        # Return the authenticated user
        return user
    
    def create_access_token(self, user_id: str, expires_delta: Optional[int] = None) -> str:
        """
        Create JWT access token for a user
        
        Args:
            user_id: User ID
            expires_delta: Token expiration time in seconds
            
        Returns:
            str: JWT access token
        """
        # Set expiration
        if expires_delta:
            expire = datetime.now() + timedelta(seconds=expires_delta)
        else:
            expire = datetime.now() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        
        # Create token payload
        to_encode = {
            "sub": str(user_id),
            "exp": expire
        }
        
        # Encode token
        encoded_jwt = jwt.encode(
            to_encode, 
            settings.SECRET_KEY, 
            algorithm=settings.ALGORITHM
        )
        
        return encoded_jwt
    
    async def activate_user(self, user_id: str) -> User:
        """
        Activate a user
        
        Args:
            user_id: The user ID
            
        Returns:
            User: The activated user
        """
        # Get user
        user = await self.user_repo.get(user_id)
        if not user:
            raise ValueError(f"User with ID {user_id} not found")
        
        # Update status
        user.status = UserStatus.ACTIVE
        updated_user = await self.user_repo.update(user_id, user)
        
        # Audit log
        audit_log(
            message=f"Activated user {user.username}",
            resource_type="user",
            resource_id=user_id,
            action_type="activate_user"
        )
        
        return updated_user
    
    async def deactivate_user(self, user_id: str) -> User:
        """
        Deactivate a user
        
        Args:
            user_id: The user ID
            
        Returns:
            User: The deactivated user
        """
        # Get user
        user = await self.user_repo.get(user_id)
        if not user:
            raise ValueError(f"User with ID {user_id} not found")
        
        # Update status
        user.status = UserStatus.INACTIVE
        updated_user = await self.user_repo.update(user_id, user)
        
        # Audit log
        audit_log(
            message=f"Deactivated user {user.username}",
            resource_type="user",
            resource_id=user_id,
            action_type="deactivate_user"
        )
        
        return updated_user
    
    async def add_user_device(self, user_id: str, device_data: UserDevice) -> bool:
        """
        Add a device to a user's account
        
        Args:
            user_id: The user ID
            device_data: Device information
            
        Returns:
            bool: True if successful
        """
        # Check if user exists
        user = await self.user_repo.get(user_id)
        if not user:
            raise ValueError(f"User with ID {user_id} not found")
        
        # Add device
        result = await self.user_repo.add_device(user_id, device_data.dict())
        
        # Audit log
        if result:
            audit_log(
                message=f"Added device to user {user.username}",
                resource_type="user",
                resource_id=user_id,
                action_type="add_device",
                metadata={"device_id": device_data.device_id}
            )
        
        return result
    
    async def update_notification_settings(
        self,
        user_id: str,
        settings_data: Dict[str, Any]
    ) -> User:
        """
        Update notification settings for a user
        
        Args:
            user_id: The user ID
            settings_data: Notification settings
            
        Returns:
            User: The updated user
        """
        # Get user
        user = await self.user_repo.get(user_id)
        if not user:
            raise ValueError(f"User with ID {user_id} not found")
        
        # Update notification settings
        if "notification_enabled" in settings_data:
            user.notification_enabled = settings_data["notification_enabled"]
        
        if "webpush_enabled" in settings_data:
            user.webpush_enabled = settings_data["webpush_enabled"]
        
        if "email_notification_enabled" in settings_data:
            user.email_notification_enabled = settings_data["email_notification_enabled"]
        
        if "quiet_hours_start" in settings_data:
            user.quiet_hours_start = settings_data["quiet_hours_start"]
        
        if "quiet_hours_end" in settings_data:
            user.quiet_hours_end = settings_data["quiet_hours_end"]
        
        # Save updates
        updated_user = await self.user_repo.update(user_id, user)
        
        # Audit log
        audit_log(
            message=f"Updated notification settings for {user.username}",
            resource_type="user",
            resource_id=user_id,
            action_type="update_notification_settings"
        )
        
        return updated_user
    
    async def get_user_stats(self, user_id: str) -> Dict[str, Any]:
        """
        Get statistics for a user
        
        Args:
            user_id: The user ID
            
        Returns:
            Dict: User statistics
        """
        # TODO: Implement actual stats calculation
        return {
            "total_notifications": 0,
            "open_rate": 0.0,
            "click_rate": 0.0,
            "last_interaction": None
        }
