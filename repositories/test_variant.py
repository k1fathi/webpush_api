import uuid
from typing import List, Optional

from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from db.session import get_session
from models.domain.test_variant import TestVariantModel
from models.schemas.test_variant import TestVariant
from repositories.base import BaseRepository

class TestVariantRepository(BaseRepository):
    """Repository for test variant operations"""
    
    async def create(self, variant: TestVariant) -> TestVariant:
        """Create a new test variant"""
        async with get_session() as session:
            db_variant = TestVariantModel(
                id=str(uuid.uuid4()) if not variant.id else variant.id,
                ab_test_id=variant.ab_test_id,
                template_id=variant.template_id,
                name=variant.name,
                sent_count=variant.sent_count,
                opened_count=variant.opened_count,
                clicked_count=variant.clicked_count
            )
            session.add(db_variant)
            await session.commit()
            await session.refresh(db_variant)
            return TestVariant.from_orm(db_variant)
    
    async def get(self, variant_id: str) -> Optional[TestVariant]:
        """Get a test variant by ID"""
        async with get_session() as session:
            result = await session.execute(
                select(TestVariantModel).where(TestVariantModel.id == variant_id)
            )
            db_variant = result.scalars().first()
            return TestVariant.from_orm(db_variant) if db_variant else None
    
    async def get_by_test(self, ab_test_id: str) -> List[TestVariant]:
        """Get all variants for a test"""
        async with get_session() as session:
            result = await session.execute(
                select(TestVariantModel).where(TestVariantModel.ab_test_id == ab_test_id)
            )
            db_variants = result.scalars().all()
            return [TestVariant.from_orm(db_variant) for db_variant in db_variants]
    
    async def update(self, variant_id: str, variant: TestVariant) -> TestVariant:
        """Update a test variant"""
        async with get_session() as session:
            result = await session.execute(
                select(TestVariantModel).where(TestVariantModel.id == variant_id)
            )
            db_variant = result.scalars().first()
            if not db_variant:
                raise ValueError(f"Test variant with ID {variant_id} not found")
                
            # Update the attributes
            db_variant.name = variant.name
            db_variant.sent_count = variant.sent_count
            db_variant.opened_count = variant.opened_count
            db_variant.clicked_count = variant.clicked_count
            
            await session.commit()
            await session.refresh(db_variant)
            return TestVariant.from_orm(db_variant)
    
    async def increment_counters(self, variant_id: str, sent=0, opened=0, clicked=0) -> bool:
        """Increment the counters for a test variant"""
        async with get_session() as session:
            result = await session.execute(
                select(TestVariantModel).where(TestVariantModel.id == variant_id)
            )
            db_variant = result.scalars().first()
            if not db_variant:
                return False
                
            # Increment counters
            if sent:
                db_variant.sent_count += sent
            if opened:
                db_variant.opened_count += opened
            if clicked:
                db_variant.clicked_count += clicked
                
            await session.commit()
            return True
    
    async def delete(self, variant_id: str) -> bool:
        """Delete a test variant"""
        async with get_session() as session:
            result = await session.execute(
                select(TestVariantModel).where(TestVariantModel.id == variant_id)
            )
            db_variant = result.scalars().first()
            if db_variant:
                await session.delete(db_variant)
                await session.commit()
                return True
            return False
    
    async def count_by_test(self, ab_test_id: str) -> int:
        """Count the number of variants for a test"""
        async with get_session() as session:
            result = await session.execute(
                select(func.count()).where(TestVariantModel.ab_test_id == ab_test_id)
            )
            return result.scalar() or 0
