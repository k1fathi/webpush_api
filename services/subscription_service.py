"""Service for managing user webpush subscriptions"""
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any

from sqlalchemy import select, update, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.expression import true

from models.domain import UserModel
from models.schemas.user import UserStatus


async def get_all_subscriptions(
    db: AsyncSession, 
    skip: int = 0, 
    limit: int = 100,
    active_only: bool = True
) -> List[Dict[str, Any]]:
    """
    Get all subscriptions with pagination
    
    Args:
        db: Database session
        skip: Number of records to skip for pagination
        limit: Maximum records to return
        active_only: If True, only return subscriptions of active users
    
    Returns:
        List of subscription information with user details
    """
    query = select(
        UserModel.id, 
        UserModel.email, 
        UserModel.username,
        UserModel.subscription_info,
        UserModel.last_seen,
        UserModel.webpush_enabled
    )
    
    if active_only:
        query = query.where(
            UserModel.is_active == true(),
            UserModel.webpush_enabled == true(),
            UserModel.subscription_info.cast(str) != '{}'  # Only users with subscription info
        )
    
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    subscriptions = result.mappings().all()
    
    return [dict(sub) for sub in subscriptions]


async def get_subscription_by_user_id(
    db: AsyncSession, 
    user_id: uuid.UUID
) -> Optional[Dict[str, Any]]:
    """
    Get subscription for a specific user
    
    Args:
        db: Database session
        user_id: User ID to find subscription for
        
    Returns:
        User's subscription information or None if not found
    """
    query = select(
        UserModel.id,
        UserModel.email,
        UserModel.subscription_info,
        UserModel.webpush_enabled
    ).where(UserModel.id == user_id)
    
    result = await db.execute(query)
    user = result.mappings().one_or_none()
    
    return dict(user) if user else None


async def get_active_subscription_count(db: AsyncSession) -> int:
    """
    Get count of active subscriptions
    
    Args:
        db: Database session
        
    Returns:
        Count of active subscriptions
    """
    query = select(func.count()).select_from(UserModel).where(
        UserModel.is_active == true(),
        UserModel.webpush_enabled == true(),
        UserModel.subscription_info.cast(str) != '{}'
    )
    
    result = await db.execute(query)
    count = result.scalar_one()
    
    return count


async def update_subscription(
    db: AsyncSession,
    user_id: uuid.UUID,
    subscription_data: Dict[str, Any]
) -> bool:
    """
    Update a user's subscription info
    
    Args:
        db: Database session
        user_id: User ID to update
        subscription_data: New subscription data
        
    Returns:
        True if update was successful
    """
    stmt = update(UserModel).where(
        UserModel.id == user_id
    ).values(
        subscription_info=subscription_data,
        updated_at=datetime.utcnow()
    )
    
    result = await db.execute(stmt)
    await db.commit()
    
    return result.rowcount > 0


async def get_subscriptions_by_segment_id(
    db: AsyncSession,
    segment_id: uuid.UUID,
    skip: int = 0,
    limit: int = 100
) -> List[Dict[str, Any]]:
    """
    Get subscriptions for users in a specific segment
    
    Args:
        db: Database session
        segment_id: Segment ID
        skip: Number of records to skip
        limit: Maximum number of records to return
        
    Returns:
        List of user subscriptions in the segment
    """
    # Query using the user_segment association table
    query = select(
        UserModel.id,
        UserModel.email,
        UserModel.subscription_info,
        UserModel.webpush_enabled
    ).select_from(UserModel).join(
        "segments"
    ).where(
        UserModel.is_active == true(),
        UserModel.webpush_enabled == true(),
        UserModel.subscription_info.cast(str) != '{}',
        UserModel.segments.any(id=segment_id)
    ).offset(skip).limit(limit)
    
    result = await db.execute(query)
    subscriptions = result.mappings().all()
    
    return [dict(sub) for sub in subscriptions]
