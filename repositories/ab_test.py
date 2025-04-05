import uuid
from datetime import datetime
from typing import Dict, List, Optional, Union

from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from db.session import get_session
from models.domain.ab_test import AbTestModel
from models.schemas.ab_test import AbTest
from repositories.base import BaseRepository

class AbTestRepository(BaseRepository):
    """Repository for A/B test operations"""
    
    async def create(self, ab_test: AbTest) -> AbTest:
        """Create a new A/B test"""
        async with get_session() as session:
            db_ab_test = AbTestModel(
                id=str(uuid.uuid4()) if not ab_test.id else ab_test.id,
                campaign_id=ab_test.campaign_id,
                name=ab_test.name,
                description=ab_test.description,
                variant_count=ab_test.variant_count,
                winning_criteria=ab_test.winning_criteria,
                start_date=ab_test.start_date,
                end_date=ab_test.end_date
            )
            session.add(db_ab_test)
            await session.commit()
            await session.refresh(db_ab_test)
            return AbTest.from_orm(db_ab_test)
    
    async def get(self, ab_test_id: str) -> Optional[AbTest]:
        """Get an A/B test by ID"""
        async with get_session() as session:
            result = await session.execute(
                select(AbTestModel).where(AbTestModel.id == ab_test_id)
            )
            db_ab_test = result.scalars().first()
            return AbTest.from_orm(db_ab_test) if db_ab_test else None
    
    async def update(self, ab_test_id: str, ab_test: AbTest) -> AbTest:
        """Update an A/B test"""
        async with get_session() as session:
            result = await session.execute(
                select(AbTestModel).where(AbTestModel.id == ab_test_id)
            )
            db_ab_test = result.scalars().first()
            if not db_ab_test:
                raise ValueError(f"A/B test with ID {ab_test_id} not found")
                
            # Update attributes
            db_ab_test.name = ab_test.name
            db_ab_test.description = ab_test.description
            db_ab_test.variant_count = ab_test.variant_count
            db_ab_test.winning_criteria = ab_test.winning_criteria
            db_ab_test.start_date = ab_test.start_date
            db_ab_test.end_date = ab_test.end_date
            
            await session.commit()
            await session.refresh(db_ab_test)
            return AbTest.from_orm(db_ab_test)
    
    async def delete(self, ab_test_id: str) -> bool:
        """Delete an A/B test"""
        async with get_session() as session:
            result = await session.execute(
                select(AbTestModel).where(AbTestModel.id == ab_test_id)
            )
            db_ab_test = result.scalars().first()
            if db_ab_test:
                await session.delete(db_ab_test)
                await session.commit()
                return True
            return False
    
    async def get_by_campaign(self, campaign_id: str) -> List[AbTest]:
        """Get all A/B tests for a campaign"""
        async with get_session() as session:
            result = await session.execute(
                select(AbTestModel).where(AbTestModel.campaign_id == campaign_id)
            )
            db_ab_tests = result.scalars().all()
            return [AbTest.from_orm(db_test) for db_test in db_ab_tests]
    
    async def get_active_tests(self) -> List[AbTest]:
        """Get all active A/B tests (started but not yet ended)"""
        current_time = datetime.now()
        async with get_session() as session:
            result = await session.execute(
                select(AbTestModel).where(
                    and_(
                        AbTestModel.start_date <= current_time,
                        AbTestModel.end_date == None
                    )
                )
            )
            db_ab_tests = result.scalars().all()
            return [AbTest.from_orm(db_test) for db_test in db_ab_tests]
    
    async def get_completed_tests(self) -> List[AbTest]:
        """Get all completed A/B tests"""
        async with get_session() as session:
            result = await session.execute(
                select(AbTestModel).where(AbTestModel.end_date != None)
            )
            db_ab_tests = result.scalars().all()
            return [AbTest.from_orm(db_test) for db_test in db_ab_tests]
