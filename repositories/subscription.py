from typing import Dict, List, Optional, Any, Union
from uuid import UUID
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import desc, func

from models.domain.subscription import SubscriptionModel
from models.schemas.subscription import SubscriptionCreate, SubscriptionRead, SubscriptionUpdate, SubscriptionStats

class SubscriptionRepository:
    """Repository for subscription operations"""
    
    def __init__(self, db: Optional[Session] = None):
        self.db = db
    
    def create(self, subscription: SubscriptionCreate) -> SubscriptionRead:
        """Create a new subscription"""
        db_subscription = SubscriptionModel(
            user_id=subscription.user_id,
            endpoint=subscription.endpoint,
            p256dh=subscription.p256dh,
            auth=subscription.auth,
            user_agent=subscription.user_agent,
            browser_name=subscription.browser_name,
            browser_version=subscription.browser_version,
            os_name=subscription.os_name,
            os_version=subscription.os_version,
            device_type=subscription.device_type,
            screen_resolution=subscription.screen_resolution,
            referrer=subscription.referrer,
            subscription_context=subscription.subscription_context,
            permission_status=subscription.permission_status,
            frequency_cap_daily=subscription.frequency_cap_daily,
            quiet_hours_start=subscription.quiet_hours_start,
            quiet_hours_end=subscription.quiet_hours_end,
            preferred_topics=subscription.preferred_topics
        )
        
        self.db.add(db_subscription)
        self.db.commit()
        self.db.refresh(db_subscription)
        
        return SubscriptionRead.from_orm(db_subscription)
    
    def get(self, subscription_id: Union[UUID, str]) -> Optional[SubscriptionRead]:
        """Get a subscription by ID"""
        if isinstance(subscription_id, str):
            subscription_id = UUID(subscription_id)
        
        db_subscription = self.db.query(SubscriptionModel).filter(SubscriptionModel.id == subscription_id).first()
        if db_subscription is None:
            return None
        
        return SubscriptionRead.from_orm(db_subscription)
    
    def update(self, subscription_id: Union[UUID, str], subscription: SubscriptionUpdate) -> Optional[SubscriptionRead]:
        """Update an existing subscription"""
        if isinstance(subscription_id, str):
            subscription_id = UUID(subscription_id)
        
        db_subscription = self.db.query(SubscriptionModel).filter(SubscriptionModel.id == subscription_id).first()
        if db_subscription is None:
            return None
        
        # Update fields
        update_data = subscription.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_subscription, key, value)
        
        # Update the updated_at timestamp
        db_subscription.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(db_subscription)
        
        return SubscriptionRead.from_orm(db_subscription)
    
    def delete(self, subscription_id: Union[UUID, str]) -> bool:
        """Delete a subscription"""
        if isinstance(subscription_id, str):
            subscription_id = UUID(subscription_id)
        
        db_subscription = self.db.query(SubscriptionModel).filter(SubscriptionModel.id == subscription_id).first()
        if db_subscription is None:
            return False
        
        self.db.delete(db_subscription)
        self.db.commit()
        
        return True
    
    def list(
        self,
        skip: int = 0,
        limit: int = 100,
        filters: Dict[str, Any] = None
    ) -> List[SubscriptionRead]:
        """List subscriptions with optional filtering"""
        query = self.db.query(SubscriptionModel)
        
        # Apply filters if provided
        if filters:
            for key, value in filters.items():
                if hasattr(SubscriptionModel, key):
                    query = query.filter(getattr(SubscriptionModel, key) == value)
        
        # Apply pagination
        db_subscriptions = query.offset(skip).limit(limit).all()
        
        return [SubscriptionRead.from_orm(subscription) for subscription in db_subscriptions]
    
    def count(self, filters: Dict[str, Any] = None) -> int:
        """Count subscriptions with optional filtering"""
        query = self.db.query(SubscriptionModel)
        
        # Apply filters if provided
        if filters:
            for key, value in filters.items():
                if hasattr(SubscriptionModel, key):
                    query = query.filter(getattr(SubscriptionModel, key) == value)
        
        return query.count()
    
    def get_by_user(self, user_id: Union[UUID, str]) -> List[SubscriptionRead]:
        """Get all subscriptions for a specific user"""
        if isinstance(user_id, str):
            user_id = UUID(user_id)
        
        db_subscriptions = (
            self.db.query(SubscriptionModel)
            .filter(SubscriptionModel.user_id == user_id)
            .order_by(desc(SubscriptionModel.created_at))
            .all()
        )
        
        return [SubscriptionRead.from_orm(subscription) for subscription in db_subscriptions]
    
    def get_by_endpoint(self, endpoint: str) -> Optional[SubscriptionRead]:
        """Get a subscription by endpoint URL"""
        db_subscription = self.db.query(SubscriptionModel).filter(SubscriptionModel.endpoint == endpoint).first()
        if db_subscription is None:
            return None
        
        return SubscriptionRead.from_orm(db_subscription)
    
    def mark_notified(self, subscription_id: Union[UUID, str]) -> bool:
        """Mark a subscription as notified (update last_notified_at)"""
        if isinstance(subscription_id, str):
            subscription_id = UUID(subscription_id)
        
        db_subscription = self.db.query(SubscriptionModel).filter(SubscriptionModel.id == subscription_id).first()
        if db_subscription is None:
            return False
        
        db_subscription.last_notified_at = datetime.utcnow()
        db_subscription.notification_count += 1
        
        self.db.commit()
        return True
    
    def increment_successful_delivery(self, subscription_id: Union[UUID, str], delivery_time_ms: Optional[int] = None) -> bool:
        """Increment successful delivery count and optionally update average delivery time"""
        if isinstance(subscription_id, str):
            subscription_id = UUID(subscription_id)
        
        db_subscription = self.db.query(SubscriptionModel).filter(SubscriptionModel.id == subscription_id).first()
        if db_subscription is None:
            return False
        
        db_subscription.successful_delivery_count += 1
        
        # Update average delivery time if provided
        if delivery_time_ms is not None:
            if db_subscription.average_delivery_time is None:
                db_subscription.average_delivery_time = delivery_time_ms
            else:
                # Calculate new average
                total = db_subscription.average_delivery_time * (db_subscription.successful_delivery_count - 1)
                new_avg = (total + delivery_time_ms) / db_subscription.successful_delivery_count
                db_subscription.average_delivery_time = int(new_avg)
        
        self.db.commit()
        return True
    
    def increment_failed_delivery(self, subscription_id: Union[UUID, str]) -> bool:
        """Increment failed delivery count"""
        if isinstance(subscription_id, str):
            subscription_id = UUID(subscription_id)
        
        db_subscription = self.db.query(SubscriptionModel).filter(SubscriptionModel.id == subscription_id).first()
        if db_subscription is None:
            return False
        
        db_subscription.failed_delivery_count += 1
        
        self.db.commit()
        return True
    
    def update_permission_status(self, subscription_id: Union[UUID, str], status: str) -> bool:
        """Update permission status for a subscription"""
        if isinstance(subscription_id, str):
            subscription_id = UUID(subscription_id)
        
        db_subscription = self.db.query(SubscriptionModel).filter(SubscriptionModel.id == subscription_id).first()
        if db_subscription is None:
            return False
        
        db_subscription.permission_status = status
        db_subscription.permission_updated_at = datetime.utcnow()
        
        self.db.commit()
        return True
    
    def get_inactive_subscriptions(self, days: int = 90) -> List[SubscriptionRead]:
        """Get subscriptions that haven't been used in a specified number of days"""
        cutoff_date = datetime.utcnow() - datetime.timedelta(days=days)
        
        db_subscriptions = (
            self.db.query(SubscriptionModel)
            .filter(
                (SubscriptionModel.last_notified_at < cutoff_date) | 
                (SubscriptionModel.last_notified_at.is_(None) & (SubscriptionModel.created_at < cutoff_date))
            )
            .all()
        )
        
        return [SubscriptionRead.from_orm(subscription) for subscription in db_subscriptions]
    
    def get_subscription_stats(self) -> SubscriptionStats:
        """Get subscription statistics"""
        total = self.db.query(func.count(SubscriptionModel.id)).scalar() or 0
        active = self.db.query(func.count(SubscriptionModel.id)).filter(SubscriptionModel.is_active == True).scalar() or 0
        
        # Get browser stats
        browser_stats = (
            self.db.query(
                SubscriptionModel.browser_name,
                func.count(SubscriptionModel.id)
            )
            .filter(SubscriptionModel.browser_name.isnot(None))
            .group_by(SubscriptionModel.browser_name)
            .all()
        )
        
        # Get OS stats
        os_stats = (
            self.db.query(
                SubscriptionModel.os_name,
                func.count(SubscriptionModel.id)
            )
            .filter(SubscriptionModel.os_name.isnot(None))
            .group_by(SubscriptionModel.os_name)
            .all()
        )
        
        # Get device type stats
        device_stats = (
            self.db.query(
                SubscriptionModel.device_type,
                func.count(SubscriptionModel.id)
            )
            .filter(SubscriptionModel.device_type.isnot(None))
            .group_by(SubscriptionModel.device_type)
            .all()
        )
        
        # Calculate average notifications per subscription
        total_notifications = self.db.query(func.sum(SubscriptionModel.notification_count)).scalar() or 0
        avg_notifications = total_notifications / total if total > 0 else 0
        
        # Calculate average delivery rate
        total_success = self.db.query(func.sum(SubscriptionModel.successful_delivery_count)).scalar() or 0
        total_failed = self.db.query(func.sum(SubscriptionModel.failed_delivery_count)).scalar() or 0
        total_attempts = total_success + total_failed
        avg_delivery_rate = total_success / total_attempts if total_attempts > 0 else 0
        
        # Convert to dictionaries
        browser_dict = {browser: count for browser, count in browser_stats}
        os_dict = {os: count for os, count in os_stats}
        device_dict = {device: count for device, count in device_stats}
        
        return SubscriptionStats(
            total_subscriptions=total,
            active_subscriptions=active,
            subscriptions_by_browser=browser_dict,
            subscriptions_by_os=os_dict,
            subscriptions_by_device_type=device_dict,
            average_notifications_per_subscription=avg_notifications,
            average_delivery_rate=avg_delivery_rate
        )