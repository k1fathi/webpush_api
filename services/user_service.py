from typing import List, Optional, Dict
from datetime import datetime
from core.security import get_password_hash, verify_password
from db.repositories.user_repository import UserRepository
from schemas.user_schema import UserCreate, UserUpdate, UserInDB

class UserService:
    def __init__(self, repository: UserRepository):
        self.repository = repository

    async def create_user(self, user_data: Dict) -> User:
        if "password" in user_data:
            user_data["password_hash"] = get_password_hash(user_data.pop("password"))
        
        role_ids = user_data.pop("role_ids", [])
        segment_ids = user_data.pop("segment_ids", [])
        
        return await self.repository.create(user_data, role_ids, segment_ids)

    async def authenticate(self, email: str, password: str) -> Optional[User]:
        user = await self.repository.get_by_email(email)
        if user and verify_password(password, user.password_hash):
            await self.repository.update_last_login(user.user_id)
            return user
        return None

    async def get_user(self, user_id: int) -> Optional[User]:
        return await self.repository.get_by_id(user_id)

    async def update_user(self, user_id: int, user_data: Dict) -> Optional[User]:
        if "password" in user_data:
            user_data["password_hash"] = get_password_hash(user_data.pop("password"))
        return await self.repository.update(user_id, user_data)
