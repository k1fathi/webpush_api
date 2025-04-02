import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

from sqlalchemy import select, func, and_, or_, desc
from sqlalchemy.ext.asyncio import AsyncSession

from db.session import get_session
from models.domain.trigger import TriggerModel, TriggerExecutionModel
from models.trigger import Trigger, TriggerStatus, TriggerAction
from repositories.base import BaseRepository

class TriggerRepository(BaseRepository):
    """Repository for trigger operations"""
    
    async def create(self, trigger: Trigger) -> Trigger:
        """Create a new trigger"""
        async with get_session() as session:
            db_trigger = TriggerModel(
                id=str(uuid.uuid4()) if not trigger.id else trigger.id,
                name=trigger.name,
                description=trigger.description,
                trigger_type=trigger.trigger_type,
                status=trigger.status,
                rules=trigger.rules,
                schedule=trigger.schedule,
                action=trigger.action,
                trigger_count=0,
                error_count=0,
                metadata=trigger.metadata,
                cooldown_period=trigger.cooldown_period,
                max_triggers_per_day=trigger.max_triggers_per_day,
                enabled=trigger.enabled
            )
            session.add(db_trigger)
            await session.commit()
            await session.refresh(db_trigger)
            return Trigger.from_orm(db_trigger)

    async def get(self, trigger_id: str) -> Optional[Trigger]:
        """Get a trigger by ID"""
        async with get_session() as session:
            result = await session.execute(
                select(TriggerModel).where(TriggerModel.id == trigger_id)
            )
            db_trigger = result.scalars().first()
            return Trigger.from_orm(db_trigger) if db_trigger else None

    async def update(self, trigger_id: str, trigger: Trigger) -> Trigger:
        """Update a trigger"""
        async with get_session() as session:
            result = await session.execute(
                select(TriggerModel).where(TriggerModel.id == trigger_id)
            )
            db_trigger = result.scalars().first()
            if not db_trigger:
                raise ValueError(f"Trigger with ID {trigger_id} not found")

            # Update fields
            db_trigger.name = trigger.name
            db_trigger.description = trigger.description
            db_trigger.rules = trigger.rules
            db_trigger.schedule = trigger.schedule
            db_trigger.action = trigger.action
            db_trigger.status = trigger.status
            db_trigger.metadata = trigger.metadata
            db_trigger.cooldown_period = trigger.cooldown_period
            db_trigger.max_triggers_per_day = trigger.max_triggers_per_day
            db_trigger.enabled = trigger.enabled
            db_trigger.updated_at = datetime.now()

            await session.commit()
            await session.refresh(db_trigger)
            return Trigger.from_orm(db_trigger)

    async def delete(self, trigger_id: str) -> bool:
        """Delete a trigger"""
        async with get_session() as session:
            result = await session.execute(
                select(TriggerModel).where(TriggerModel.id == trigger_id)
            )
            db_trigger = result.scalars().first()
            if db_trigger:
                await session.delete(db_trigger)
                await session.commit()
                return True
            return False

    async def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        type_filter: Optional[str] = None,
        status_filter: Optional[str] = None,
        enabled_only: bool = False
    ) -> List[Trigger]:
        """Get all triggers with filtering"""
        async with get_session() as session:
            query = select(TriggerModel)
            
            if type_filter:
                query = query.where(TriggerModel.trigger_type == type_filter)
            if status_filter:
                query = query.where(TriggerModel.status == status_filter)
            if enabled_only:
                query = query.where(TriggerModel.enabled == True)
                
            query = query.order_by(desc(TriggerModel.updated_at))
            query = query.offset(skip).limit(limit)
            
            result = await session.execute(query)
            db_triggers = result.scalars().all()
            return [Trigger.from_orm(t) for t in db_triggers]

    async def record_execution(
        self,
        trigger_id: str,
        success: bool,
        action_result: Optional[Dict] = None,
        error: Optional[str] = None
    ) -> bool:
        """Record a trigger execution"""
        async with get_session() as session:
            # Create execution record
            execution = TriggerExecutionModel(
                id=str(uuid.uuid4()),
                trigger_id=trigger_id,
                success=success,
                action_result=action_result,
                error=error
            )
            session.add(execution)
            
            # Update trigger counters
            result = await session.execute(
                select(TriggerModel).where(TriggerModel.id == trigger_id)
            )
            db_trigger = result.scalars().first()
            if db_trigger:
                db_trigger.trigger_count += 1
                if not success:
                    db_trigger.error_count += 1
                db_trigger.last_triggered_at = datetime.now()
            
            await session.commit()
            return True

    async def get_executions(
        self,
        trigger_id: str,
        limit: int = 100
    ) -> List[Dict]:
        """Get execution history for a trigger"""
        async with get_session() as session:
            result = await session.execute(
                select(TriggerExecutionModel)
                .where(TriggerExecutionModel.trigger_id == trigger_id)
                .order_by(desc(TriggerExecutionModel.executed_at))
                .limit(limit)
            )
            executions = result.scalars().all()
            return [{
                "id": str(ex.id),
                "trigger_id": str(ex.trigger_id),
                "executed_at": ex.executed_at,
                "success": ex.success,
                "action_result": ex.action_result,
                "error": ex.error
            } for ex in executions]

    async def get_active_triggers(self) -> List[Trigger]:
        """Get all active and enabled triggers"""
        async with get_session() as session:
            result = await session.execute(
                select(TriggerModel)
                .where(and_(
                    TriggerModel.enabled == True,
                    TriggerModel.status == TriggerStatus.ACTIVE
                ))
            )
            db_triggers = result.scalars().all()
            return [Trigger.from_orm(t) for t in db_triggers]
