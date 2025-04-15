from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import desc

from models.domain.web_push_event import WebPushEventModel
from models.schemas.web_push_event import WebPushEventCreate, WebPushEvent, WebPushEventUpdate

class WebPushEventRepository:
    """Repository for web push event operations"""
    
    def __init__(self, db: Optional[Session] = None):
        self.db = db
    
    def create(self, event: WebPushEventCreate) -> WebPushEvent:
        """Create a new web push event"""
        db_event = WebPushEventModel(
            event_type=event.event_type,
            event_data=event.event_data,
            notification_id=event.notification_id,
            subscription_id=event.subscription_id,
            user_id=event.user_id,
            campaign_id=event.campaign_id,
            page_url=event.page_url,
            referrer=event.referrer,
            action_id=event.action_id,
            user_agent=event.user_agent,
            browser_name=event.browser_name,
            browser_version=event.browser_version,
            os_name=event.os_name,
            os_version=event.os_version,
            device_type=event.device_type,
            screen_resolution=event.screen_resolution,
            ip_address=event.ip_address,
            country=event.country,
            region=event.region,
            city=event.city,
            time_since_sent=event.time_since_sent,
            time_since_delivery=event.time_since_delivery,
            processing_time=event.processing_time,
            error_message=event.error_message,
            error_code=event.error_code
        )
        
        self.db.add(db_event)
        self.db.commit()
        self.db.refresh(db_event)
        
        return WebPushEvent.from_orm(db_event)
    
    def get(self, event_id: Union[UUID, str]) -> Optional[WebPushEvent]:
        """Get a web push event by ID"""
        if isinstance(event_id, str):
            event_id = UUID(event_id)
        
        db_event = self.db.query(WebPushEventModel).filter(WebPushEventModel.id == event_id).first()
        if db_event is None:
            return None
        
        return WebPushEvent.from_orm(db_event)
    
    def update(self, event_id: Union[UUID, str], event: WebPushEventUpdate) -> Optional[WebPushEvent]:
        """Update an existing web push event"""
        if isinstance(event_id, str):
            event_id = UUID(event_id)
        
        db_event = self.db.query(WebPushEventModel).filter(WebPushEventModel.id == event_id).first()
        if db_event is None:
            return None
        
        # Update fields
        update_data = event.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_event, key, value)
        
        self.db.commit()
        self.db.refresh(db_event)
        
        return WebPushEvent.from_orm(db_event)
    
    def delete(self, event_id: Union[UUID, str]) -> bool:
        """Delete a web push event"""
        if isinstance(event_id, str):
            event_id = UUID(event_id)
        
        db_event = self.db.query(WebPushEventModel).filter(WebPushEventModel.id == event_id).first()
        if db_event is None:
            return False
        
        self.db.delete(db_event)
        self.db.commit()
        
        return True
    
    def list(
        self,
        skip: int = 0,
        limit: int = 100,
        filters: Dict[str, Any] = None
    ) -> List[WebPushEvent]:
        """List web push events with optional filtering"""
        query = self.db.query(WebPushEventModel)
        
        # Apply filters if provided
        if filters:
            for key, value in filters.items():
                if hasattr(WebPushEventModel, key):
                    query = query.filter(getattr(WebPushEventModel, key) == value)
        
        # Sort by most recent first
        query = query.order_by(desc(WebPushEventModel.event_timestamp))
        
        # Apply pagination
        db_events = query.offset(skip).limit(limit).all()
        
        return [WebPushEvent.from_orm(event) for event in db_events]
    
    def count(self, filters: Dict[str, Any] = None) -> int:
        """Count web push events with optional filtering"""
        query = self.db.query(WebPushEventModel)
        
        # Apply filters if provided
        if filters:
            for key, value in filters.items():
                if hasattr(WebPushEventModel, key):
                    query = query.filter(getattr(WebPushEventModel, key) == value)
        
        return query.count()
    
    def get_by_user(self, user_id: Union[UUID, str], limit: int = 50) -> List[WebPushEvent]:
        """Get web push events for a specific user"""
        if isinstance(user_id, str):
            user_id = UUID(user_id)
        
        db_events = (
            self.db.query(WebPushEventModel)
            .filter(WebPushEventModel.user_id == user_id)
            .order_by(desc(WebPushEventModel.event_timestamp))
            .limit(limit)
            .all()
        )
        
        return [WebPushEvent.from_orm(event) for event in db_events]
    
    def get_by_subscription(self, subscription_id: Union[UUID, str], limit: int = 50) -> List[WebPushEvent]:
        """Get web push events for a specific subscription"""
        if isinstance(subscription_id, str):
            subscription_id = UUID(subscription_id)
        
        db_events = (
            self.db.query(WebPushEventModel)
            .filter(WebPushEventModel.subscription_id == subscription_id)
            .order_by(desc(WebPushEventModel.event_timestamp))
            .limit(limit)
            .all()
        )
        
        return [WebPushEvent.from_orm(event) for event in db_events]
    
    def get_by_notification(self, notification_id: Union[UUID, str]) -> List[WebPushEvent]:
        """Get web push events for a specific notification"""
        if isinstance(notification_id, str):
            notification_id = UUID(notification_id)
        
        db_events = (
            self.db.query(WebPushEventModel)
            .filter(WebPushEventModel.notification_id == notification_id)
            .order_by(desc(WebPushEventModel.event_timestamp))
            .all()
        )
        
        return [WebPushEvent.from_orm(event) for event in db_events]
    
    def get_by_campaign(self, campaign_id: Union[UUID, str], limit: int = 100) -> List[WebPushEvent]:
        """Get web push events for a specific campaign"""
        if isinstance(campaign_id, str):
            campaign_id = UUID(campaign_id)
        
        db_events = (
            self.db.query(WebPushEventModel)
            .filter(WebPushEventModel.campaign_id == campaign_id)
            .order_by(desc(WebPushEventModel.event_timestamp))
            .limit(limit)
            .all()
        )
        
        return [WebPushEvent.from_orm(event) for event in db_events]