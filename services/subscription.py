import logging
from datetime import datetime
from typing import List, Optional, Tuple, Dict, Any
from uuid import UUID

from fastapi import Depends
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc

from db.session import get_db
from models.domain.subscription import SubscriptionModel
from models.schemas.subscription import SubscriptionCreate, SubscriptionUpdate

logger = logging.getLogger(__name__)

class SubscriptionService:
    """Service for managing subscriptions"""
    
    def __init__(self, db: Session = Depends(get_db)):
        self.db = db
    
    async def create_subscription(self, subscription: SubscriptionCreate) -> SubscriptionModel:
        """Create a new subscription"""
        new_subscription = SubscriptionModel(
            endpoint=subscription.endpoint,
            p256dh=subscription.p256dh,
            auth=subscription.auth,
            user_id=subscription.user_id,
        )
        self.db.add(new_subscription)
        self.db.commit()
        self.db.refresh(new_subscription)
        return new_subscription
    
    async def get_subscription(self, subscription_id: str) -> Optional[SubscriptionModel]:
        """Get a subscription by ID"""
        try:
            return self.db.query(SubscriptionModel).filter(SubscriptionModel.id == UUID(subscription_id)).first()
        except ValueError:
            logger.error(f"Invalid subscription ID format: {subscription_id}")
            return None
    
    async def get_all_subscriptions(
        self, 
        skip: int = 0, 
        limit: int = 100,
        user_id: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> Tuple[List[SubscriptionModel], int]:
        """Get all subscriptions with pagination and filtering"""
        query = self.db.query(SubscriptionModel)
        
        if user_id:
            query = query.filter(SubscriptionModel.user_id == user_id)
        
        if is_active is not None:
            query = query.filter(SubscriptionModel.is_active == is_active)
            
        total = query.count()
        subscriptions = query.order_by(desc(SubscriptionModel.created_at)).offset(skip).limit(limit).all()
        
        return subscriptions, total
    
    async def update_subscription(
        self, 
        subscription_id: str, 
        subscription_data: SubscriptionUpdate
    ) -> Optional[SubscriptionModel]:
        """Update a subscription"""
        subscription = await self.get_subscription(subscription_id)
        if not subscription:
            return None
            
        update_data = subscription_data.dict(exclude_unset=True)
        if update_data:
            for key, value in update_data.items():
                setattr(subscription, key, value)
            
            subscription.updated_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(subscription)
            
        return subscription
    
    async def delete_subscription(self, subscription_id: str) -> bool:
        """Delete a subscription"""
        subscription = await self.get_subscription(subscription_id)
        if not subscription:
            return False
        
        self.db.delete(subscription)
        self.db.commit()
        return True
    
    async def update_notification_timestamp(self, subscription_id: str) -> Optional[SubscriptionModel]:
        """Update the last_notified_at timestamp"""
        subscription = await self.get_subscription(subscription_id)
        if subscription:
            subscription.last_notified_at = datetime.utcnow()
            subscription.updated_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(subscription)
        return subscription
    
    async def get_active_subscriptions_by_user(self, user_id: str) -> List[SubscriptionModel]:
        """Get all active subscriptions for a user"""
        return self.db.query(SubscriptionModel).filter(
            SubscriptionModel.user_id == user_id,
            SubscriptionModel.is_active == True
        ).all()
