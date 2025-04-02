import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union

from sqlalchemy import select, func, and_, or_, desc
from sqlalchemy.ext.asyncio import AsyncSession

from db.session import get_session
from models.domain.notification import NotificationModel
from models.notification import Notification, DeliveryStatus
from repositories.base import BaseRepository

class NotificationRepository(BaseRepository):
    """Repository for notification operations"""
    
    async def create(self, notification: Notification) -> Notification:
        """Create a new notification"""
        async with get_session() as session:
            db_notification = NotificationModel(
                id=str(uuid.uuid4()) if not notification.id else notification.id,
                campaign_id=notification.campaign_id,
                user_id=notification.user_id,
                template_id=notification.template_id,
                title=notification.title,
                body=notification.body,
                image_url=notification.image_url,
                action_url=notification.action_url,
                personalized_data=notification.personalized_data,
                sent_at=notification.sent_at,
                delivery_status=notification.delivery_status,
                delivered_at=notification.delivered_at,
                opened_at=notification.opened_at,
                clicked_at=notification.clicked_at,
                device_info=notification.device_info,
                variant_id=notification.variant_id,
                notification_type=notification.notification_type
            )
            
            session.add(db_notification)
            await session.commit()
            await session.refresh(db_notification)
            return Notification.from_orm(db_notification)
    
    async def get(self, notification_id: str) -> Optional[Notification]:
        """Get a notification by ID"""
        async with get_session() as session:
            result = await session.execute(
                select(NotificationModel).where(NotificationModel.id == notification_id)
            )
            db_notification = result.scalars().first()
            return Notification.from_orm(db_notification) if db_notification else None
    
    async def update(self, notification_id: str, notification: Notification) -> Notification:
        """Update a notification"""
        async with get_session() as session:
            result = await session.execute(
                select(NotificationModel).where(NotificationModel.id == notification_id)
            )
            db_notification = result.scalars().first()
            if not db_notification:
                raise ValueError(f"Notification with ID {notification_id} not found")
                
            # Update fields
            db_notification.title = notification.title
            db_notification.body = notification.body
            db_notification.image_url = notification.image_url
            db_notification.action_url = notification.action_url
            db_notification.personalized_data = notification.personalized_data
            db_notification.delivery_status = notification.delivery_status
            db_notification.sent_at = notification.sent_at
            db_notification.delivered_at = notification.delivered_at
            db_notification.opened_at = notification.opened_at
            db_notification.clicked_at = notification.clicked_at
            db_notification.device_info = notification.device_info
            
            await session.commit()
            await session.refresh(db_notification)
            return Notification.from_orm(db_notification)
    
    async def delete(self, notification_id: str) -> bool:
        """Delete a notification"""
        async with get_session() as session:
            result = await session.execute(
                select(NotificationModel).where(NotificationModel.id == notification_id)
            )
            db_notification = result.scalars().first()
            if db_notification:
                await session.delete(db_notification)
                await session.commit()
                return True
            return False
    
    async def get_by_user(
        self, 
        user_id: str, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Notification]:
        """Get notifications for a user"""
        async with get_session() as session:
            result = await session.execute(
                select(NotificationModel)
                .where(NotificationModel.user_id == user_id)
                .order_by(desc(NotificationModel.sent_at))
                .offset(skip)
                .limit(limit)
            )
            db_notifications = result.scalars().all()
            return [Notification.from_orm(db) for db in db_notifications]
    
    async def get_by_campaign(
        self, 
        campaign_id: str, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Notification]:
        """Get notifications for a campaign"""
        async with get_session() as session:
            result = await session.execute(
                select(NotificationModel)
                .where(NotificationModel.campaign_id == campaign_id)
                .order_by(desc(NotificationModel.sent_at))
                .offset(skip)
                .limit(limit)
            )
            db_notifications = result.scalars().all()
            return [Notification.from_orm(db) for db in db_notifications]
    
    async def mark_as_sent(self, notification_id: str) -> Optional[Notification]:
        """Mark a notification as sent"""
        async with get_session() as session:
            result = await session.execute(
                select(NotificationModel).where(NotificationModel.id == notification_id)
            )
            db_notification = result.scalars().first()
            if not db_notification:
                return None
                
            db_notification.sent_at = datetime.now()
            db_notification.delivery_status = DeliveryStatus.SENDING
            
            await session.commit()
            await session.refresh(db_notification)
            return Notification.from_orm(db_notification)
    
    async def mark_as_delivered(
        self, 
        notification_id: str, 
        device_info: Optional[Dict] = None
    ) -> Optional[Notification]:
        """Mark a notification as delivered"""
        async with get_session() as session:
            result = await session.execute(
                select(NotificationModel).where(NotificationModel.id == notification_id)
            )
            db_notification = result.scalars().first()
            if not db_notification:
                return None
                
            db_notification.delivered_at = datetime.now()
            db_notification.delivery_status = DeliveryStatus.DELIVERED
            if device_info:
                db_notification.device_info = device_info
            
            await session.commit()
            await session.refresh(db_notification)
            return Notification.from_orm(db_notification)
    
    async def mark_as_opened(self, notification_id: str) -> Optional[Notification]:
        """Mark a notification as opened"""
        async with get_session() as session:
            result = await session.execute(
                select(NotificationModel).where(NotificationModel.id == notification_id)
            )
            db_notification = result.scalars().first()
            if not db_notification:
                return None
                
            db_notification.opened_at = datetime.now()
            db_notification.delivery_status = DeliveryStatus.OPENED
            
            await session.commit()
            await session.refresh(db_notification)
            return Notification.from_orm(db_notification)
    
    async def mark_as_clicked(self, notification_id: str) -> Optional[Notification]:
        """Mark a notification as clicked"""
        async with get_session() as session:
            result = await session.execute(
                select(NotificationModel).where(NotificationModel.id == notification_id)
            )
            db_notification = result.scalars().first()
            if not db_notification:
                return None
                
            db_notification.clicked_at = datetime.now()
            db_notification.delivery_status = DeliveryStatus.CLICKED
            
            await session.commit()
            await session.refresh(db_notification)
            return Notification.from_orm(db_notification)
    
    async def mark_as_failed(
        self, 
        notification_id: str, 
        error: Optional[str] = None
    ) -> Optional[Notification]:
        """Mark a notification as failed"""
        async with get_session() as session:
            result = await session.execute(
                select(NotificationModel).where(NotificationModel.id == notification_id)
            )
            db_notification = result.scalars().first()
            if not db_notification:
                return None
                
            db_notification.delivery_status = DeliveryStatus.FAILED
            
            # Store error in device_info
            if error:
                device_info = db_notification.device_info or {}
                device_info["error"] = error
                device_info["error_time"] = datetime.now().isoformat()
                db_notification.device_info = device_info
            
            await session.commit()
            await session.refresh(db_notification)
            return Notification.from_orm(db_notification)
    
    async def get_pending_notifications(self, limit: int = 100) -> List[Notification]:
        """Get pending notifications that need to be sent"""
        async with get_session() as session:
            result = await session.execute(
                select(NotificationModel)
                .where(NotificationModel.delivery_status == DeliveryStatus.PENDING)
                .limit(limit)
            )
            db_notifications = result.scalars().all()
            return [Notification.from_orm(db) for db in db_notifications]
    
    async def get_stats_by_campaign(self, campaign_id: str) -> Dict:
        """Get notification statistics for a campaign"""
        async with get_session() as session:
            # Total notifications
            result = await session.execute(
                select(func.count(NotificationModel.id))
                .where(NotificationModel.campaign_id == campaign_id)
            )
            total = result.scalar() or 0
            
            # Delivered count
            result = await session.execute(
                select(func.count(NotificationModel.id))
                .where(
                    and_(
                        NotificationModel.campaign_id == campaign_id,
                        NotificationModel.delivery_status.in_([
                            DeliveryStatus.DELIVERED, 
                            DeliveryStatus.OPENED,
                            DeliveryStatus.CLICKED
                        ])
                    )
                )
            )
            delivered = result.scalar() or 0
            
            # Opened count
            result = await session.execute(
                select(func.count(NotificationModel.id))
                .where(
                    and_(
                        NotificationModel.campaign_id == campaign_id,
                        NotificationModel.delivery_status.in_([
                            DeliveryStatus.OPENED,
                            DeliveryStatus.CLICKED
                        ])
                    )
                )
            )
            opened = result.scalar() or 0
            
            # Clicked count
            result = await session.execute(
                select(func.count(NotificationModel.id))
                .where(
                    and_(
                        NotificationModel.campaign_id == campaign_id,
                        NotificationModel.delivery_status == DeliveryStatus.CLICKED
                    )
                )
            )
            clicked = result.scalar() or 0
            
            # Failed count
            result = await session.execute(
                select(func.count(NotificationModel.id))
                .where(
                    and_(
                        NotificationModel.campaign_id == campaign_id,
                        NotificationModel.delivery_status == DeliveryStatus.FAILED
                    )
                )
            )
            failed = result.scalar() or 0
            
            # Calculate rates
            delivery_rate = (delivered / total) if total > 0 else 0
            open_rate = (opened / delivered) if delivered > 0 else 0
            click_rate = (clicked / opened) if opened > 0 else 0
            
            return {
                "total": total,
                "delivered": delivered,
                "opened": opened,
                "clicked": clicked,
                "failed": failed,
                "delivery_rate": delivery_rate,
                "open_rate": open_rate,
                "click_rate": click_rate
            }
            
    async def count_by_campaign(self, campaign_id: str) -> int:
        """Count notifications for a campaign"""
        async with get_session() as session:
            result = await session.execute(
                select(func.count(NotificationModel.id))
                .where(NotificationModel.campaign_id == campaign_id)
            )
            return result.scalar() or 0
