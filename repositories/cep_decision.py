import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union

from sqlalchemy import select, func, and_, or_, desc
from sqlalchemy.ext.asyncio import AsyncSession

from db.session import get_session
from models.domain.cep_decision import CepDecisionModel
from models.schemas.cep_decision import CepDecision, DecisionStatus
from repositories.base import BaseRepository

class CepDecisionRepository(BaseRepository):
    """Repository for CEP decision operations"""
    
    async def create(self, decision: CepDecision) -> CepDecision:
        """Create a new CEP decision"""
        async with get_session() as session:
            db_decision = CepDecisionModel(
                id=str(uuid.uuid4()) if not decision.id else decision.id,
                user_id=decision.user_id,
                campaign_id=decision.campaign_id,
                decision_time=decision.decision_time,
                selected_channel=decision.selected_channel,
                score=decision.score,
                decision_factors=decision.decision_factors,
                status=decision.status,
                outcome=decision.outcome
            )
            session.add(db_decision)
            await session.commit()
            await session.refresh(db_decision)
            return CepDecision.from_orm(db_decision)
    
    async def get(self, decision_id: str) -> Optional[CepDecision]:
        """Get a CEP decision by ID"""
        async with get_session() as session:
            result = await session.execute(
                select(CepDecisionModel).where(CepDecisionModel.id == decision_id)
            )
            db_decision = result.scalars().first()
            return CepDecision.from_orm(db_decision) if db_decision else None
    
    async def update(self, decision_id: str, decision: CepDecision) -> CepDecision:
        """Update a CEP decision"""
        async with get_session() as session:
            result = await session.execute(
                select(CepDecisionModel).where(CepDecisionModel.id == decision_id)
            )
            db_decision = result.scalars().first()
            if not db_decision:
                raise ValueError(f"CEP decision with ID {decision_id} not found")
                
            # Update attributes
            db_decision.status = decision.status
            db_decision.outcome = decision.outcome
            
            await session.commit()
            await session.refresh(db_decision)
            return CepDecision.from_orm(db_decision)
    
    async def delete(self, decision_id: str) -> bool:
        """Delete a CEP decision"""
        async with get_session() as session:
            result = await session.execute(
                select(CepDecisionModel).where(CepDecisionModel.id == decision_id)
            )
            db_decision = result.scalars().first()
            if db_decision:
                await session.delete(db_decision)
                await session.commit()
                return True
            return False
    
    async def get_by_user(self, user_id: str, limit: int = 100) -> List[CepDecision]:
        """Get CEP decisions for a user"""
        async with get_session() as session:
            result = await session.execute(
                select(CepDecisionModel)
                .where(CepDecisionModel.user_id == user_id)
                .order_by(desc(CepDecisionModel.decision_time))
                .limit(limit)
            )
            db_decisions = result.scalars().all()
            return [CepDecision.from_orm(db_decision) for db_decision in db_decisions]
    
    async def get_by_campaign(self, campaign_id: str) -> List[CepDecision]:
        """Get CEP decisions for a campaign"""
        async with get_session() as session:
            result = await session.execute(
                select(CepDecisionModel)
                .where(CepDecisionModel.campaign_id == campaign_id)
                .order_by(desc(CepDecisionModel.decision_time))
            )
            db_decisions = result.scalars().all()
            return [CepDecision.from_orm(db_decision) for db_decision in db_decisions]
    
    async def get_by_status(self, status: DecisionStatus) -> List[CepDecision]:
        """Get CEP decisions by status"""
        async with get_session() as session:
            result = await session.execute(
                select(CepDecisionModel)
                .where(CepDecisionModel.status == status)
                .order_by(desc(CepDecisionModel.decision_time))
            )
            db_decisions = result.scalars().all()
            return [CepDecision.from_orm(db_decision) for db_decision in db_decisions]
    
    async def get_recent_decisions(self, days: int = 7) -> List[CepDecision]:
        """Get recent CEP decisions"""
        cutoff = datetime.now() - timedelta(days=days)
        async with get_session() as session:
            result = await session.execute(
                select(CepDecisionModel)
                .where(CepDecisionModel.decision_time >= cutoff)
                .order_by(desc(CepDecisionModel.decision_time))
            )
            db_decisions = result.scalars().all()
            return [CepDecision.from_orm(db_decision) for db_decision in db_decisions]
    
    async def get_channel_decision_counts(self, days: int = 30) -> Dict[str, int]:
        """Get counts of decisions by channel"""
        cutoff = datetime.now() - timedelta(days=days)
        async with get_session() as session:
            result = await session.execute(
                select(
                    CepDecisionModel.selected_channel,
                    func.count(CepDecisionModel.id)
                )
                .where(CepDecisionModel.decision_time >= cutoff)
                .group_by(CepDecisionModel.selected_channel)
            )
            return {channel: count for channel, count in result}
    
    async def get_successful_decisions(self) -> List[CepDecision]:
        """Get decisions that led to successful engagement"""
        async with get_session() as session:
            # This query would be more complex in a real application
            # For now, we'll just define "successful" as having any outcome with engagement=True
            result = await session.execute(
                select(CepDecisionModel)
                .where(
                    and_(
                        CepDecisionModel.outcome != None,
                        CepDecisionModel.status == DecisionStatus.COMPLETED
                    )
                )
                .order_by(desc(CepDecisionModel.decision_time))
            )
            db_decisions = result.scalars().all()
            
            # Filter for successful outcomes (this would be done in SQL in a real app)
            successful = []
            for decision in db_decisions:
                if (isinstance(decision.outcome, dict) and 
                    decision.outcome.get("engaged") is True):
                    successful.append(CepDecision.from_orm(decision))
                    
            return successful
