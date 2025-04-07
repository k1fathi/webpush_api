#!/usr/bin/env python
"""
Seed script to create default users for each role in the system.
This enables immediate login after system setup.
"""

import asyncio
import logging
import sys
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

# Add parent directory to path so we can import from project
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.session import get_async_session_context
from models.domain.user import UserModel
from models.domain.role import RoleModel
from models.schemas.user import UserRole, UserStatus

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

DEFAULT_USERS = [
    {
        "email": "admin@example.com",
        "username": "admin",
        "password": "admin123",  # This will be hashed
        "full_name": "Admin User",
        "role": UserRole.ADMIN,
        "is_superuser": True,
    },
    {
        "email": "marketer@example.com",
        "username": "marketer",
        "password": "marketer123",  # This will be hashed
        "full_name": "Marketing User",
        "role": UserRole.MARKETER,
        "is_superuser": False,
    },
    {
        "email": "developer@example.com",
        "username": "developer",
        "password": "developer123",  # This will be hashed
        "full_name": "Developer User",
        "role": UserRole.DEVELOPER,
        "is_superuser": False,
    },
    {
        "email": "user@example.com",
        "username": "user",
        "password": "user123",  # This will be hashed
        "full_name": "Regular User",
        "role": UserRole.USER,
        "is_superuser": False,
    },
]

def get_password_hash(password: str) -> str:
    """Hash a password for storing."""
    return pwd_context.hash(password)

async def get_role_by_name(session: AsyncSession, role_name: str) -> Optional[RoleModel]:
    """Get a role by name."""
    query = select(RoleModel).where(RoleModel.name == role_name)
    result = await session.execute(query)
    return result.scalar_one_or_none()

async def ensure_roles_exist(session: AsyncSession) -> Dict[str, RoleModel]:
    """Ensure all required roles exist."""
    roles = {}
    
    for role_enum in UserRole:
        role_name = role_enum.value
        role = await get_role_by_name(session, role_name)
        
        if not role:
            # Create the role if it doesn't exist
            logger.info(f"Creating role: {role_name}")
            role = RoleModel(
                id=uuid.uuid4(),
                name=role_name,
                description=f"Default {role_name} role",
                is_active=True
            )
            session.add(role)
            await session.flush()
            await session.refresh(role)
        
        roles[role_name] = role
    
    await session.commit()
    return roles

async def get_user_by_email(session: AsyncSession, email: str) -> Optional[UserModel]:
    """Get a user by email."""
    query = select(UserModel).where(UserModel.email == email)
    result = await session.execute(query)
    return result.scalar_one_or_none()

async def seed_users() -> None:
    """Seed default users with different roles."""
    async with get_async_session_context() as session:
        # Ensure roles exist
        roles = await ensure_roles_exist(session)
        
        # Create users
        for user_data in DEFAULT_USERS:
            email = user_data["email"]
            role_name = user_data["role"].value
            
            # Check if user already exists
            existing_user = await get_user_by_email(session, email)
            if existing_user:
                logger.info(f"User with email {email} already exists, skipping")
                continue
            
            # Hash the password
            hashed_password = get_password_hash(user_data["password"])
            
            # Create new user
            new_user = UserModel(
                id=uuid.uuid4(),
                email=email,
                username=user_data["username"],
                hashed_password=hashed_password,
                full_name=user_data["full_name"],
                is_active=True,
                is_superuser=user_data["is_superuser"],
                status=UserStatus.ACTIVE,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            session.add(new_user)
            await session.flush()
            
            # Assign role
            role = roles.get(role_name)
            if role:
                # Direct SQL approach to add role
                await session.execute(
                    "INSERT INTO user_roles (user_id, role_id) VALUES (:user_id, :role_id)",
                    {"user_id": new_user.id, "role_id": role.id}
                )
                logger.info(f"Assigned role {role_name} to user {email}")
            else:
                logger.warning(f"Role {role_name} not found, user {email} created without role")
            
            logger.info(f"Created user: {email} with role: {role_name}")
        
        # Commit all changes
        await session.commit()

async def main():
    try:
        logger.info("Starting user seeding...")
        await seed_users()
        logger.info("User seeding completed successfully!")
    except Exception as e:
        logger.error(f"Error during user seeding: {str(e)}")
        raise

if __name__ == "__main__":
    asyncio.run(main())