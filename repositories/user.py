import uuid
from typing import Dict, List, Optional, Any

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from db.session import get_session
from models.domain.user import UserModel
from repositories.base import BaseRepository

class UserRepository(BaseRepository):
    """Repository for user operations"""
    
    # ... existing code ...
    
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
