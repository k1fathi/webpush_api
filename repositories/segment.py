import uuid
import json
from datetime import datetime
from typing import Dict, List, Optional, Any

from sqlalchemy import select, func, and_, or_, desc
from sqlalchemy.ext.asyncio import AsyncSession

from db.session import get_session
from models.domain.segment import SegmentModel
from models.segment import Segment, SegmentType
from repositories.base import BaseRepository

class SegmentRepository(BaseRepository):
    """Repository for segment operations"""
    
    async def create(self, segment: Segment) -> Segment:
        """Create a new segment"""
        async with get_session() as session:
            db_segment = SegmentModel(
                id=str(uuid.uuid4()) if not segment.id else segment.id,
                name=segment.name,
                description=segment.description,
                segment_type=segment.segment_type,
                filter_criteria=segment.filter_criteria,
                user_count=segment.user_count,
                created_at=datetime.now(),
                updated_at=datetime.now(),
                last_evaluated_at=segment.last_evaluated_at,
                is_active=segment.is_active
            )
            session.add(db_segment)
            await session.commit()
            await session.refresh(db_segment)
            return Segment.from_orm(db_segment)
    
    async def get(self, segment_id: str) -> Optional[Segment]:
        """Get a segment by ID"""
        async with get_session() as session:
            result = await session.execute(
                select(SegmentModel).where(SegmentModel.id == segment_id)
            )
            db_segment = result.scalars().first()
            return Segment.from_orm(db_segment) if db_segment else None
    
    async def get_all(
        self, 
        skip: int = 0, 
        limit: int = 100,
        active_only: bool = False
    ) -> List[Segment]:
        """Get all segments with pagination"""
        async with get_session() as session:
            query = select(SegmentModel).order_by(desc(SegmentModel.updated_at))
            
            if active_only:
                query = query.where(SegmentModel.is_active == True)
                
            query = query.offset(skip).limit(limit)
            result = await session.execute(query)
            db_segments = result.scalars().all()
            return [Segment.from_orm(db) for db in db_segments]
    
    async def update(self, segment_id: str, segment: Segment) -> Segment:
        """Update a segment"""
        async with get_session() as session:
            result = await session.execute(
                select(SegmentModel).where(SegmentModel.id == segment_id)
            )
            db_segment = result.scalars().first()
            if not db_segment:
                raise ValueError(f"Segment with ID {segment_id} not found")
                
            # Update fields
            db_segment.name = segment.name
            db_segment.description = segment.description
            db_segment.filter_criteria = segment.filter_criteria
            db_segment.segment_type = segment.segment_type
            db_segment.user_count = segment.user_count
            db_segment.updated_at = datetime.now()
            db_segment.last_evaluated_at = segment.last_evaluated_at
            db_segment.is_active = segment.is_active
            
            await session.commit()
            await session.refresh(db_segment)
            return Segment.from_orm(db_segment)
    
    async def delete(self, segment_id: str) -> bool:
        """Delete a segment"""
        async with get_session() as session:
            result = await session.execute(
                select(SegmentModel).where(SegmentModel.id == segment_id)
            )
            db_segment = result.scalars().first()
            if db_segment:
                await session.delete(db_segment)
                await session.commit()
                return True
            return False
    
    async def update_user_count(self, segment_id: str, count: int) -> bool:
        """Update the user count for a segment"""
        async with get_session() as session:
            result = await session.execute(
                select(SegmentModel).where(SegmentModel.id == segment_id)
            )
            db_segment = result.scalars().first()
            if not db_segment:
                return False
                
            db_segment.user_count = count
            db_segment.last_evaluated_at = datetime.now()
            db_segment.updated_at = datetime.now()
            
            await session.commit()
            return True
    
    async def mark_as_evaluated(self, segment_id: str) -> bool:
        """Mark a segment as evaluated"""
        async with get_session() as session:
            result = await session.execute(
                select(SegmentModel).where(SegmentModel.id == segment_id)
            )
            db_segment = result.scalars().first()
            if not db_segment:
                return False
                
            db_segment.last_evaluated_at = datetime.now()
            
            await session.commit()
            return True
    
    async def search_segments(self, query: str, limit: int = 10) -> List[Segment]:
        """Search for segments by name or description"""
        search_term = f"%{query}%"
        async with get_session() as session:
            result = await session.execute(
                select(SegmentModel).where(
                    or_(
                        SegmentModel.name.ilike(search_term),
                        SegmentModel.description.ilike(search_term)
                    )
                ).limit(limit)
            )
            db_segments = result.scalars().all()
            return [Segment.from_orm(db) for db in db_segments]
    
    async def get_by_type(self, segment_type: SegmentType) -> List[Segment]:
        """Get segments by type"""
        async with get_session() as session:
            result = await session.execute(
                select(SegmentModel).where(SegmentModel.segment_type == segment_type)
            )
            db_segments = result.scalars().all()
            return [Segment.from_orm(db) for db in db_segments]
    
    async def count_segments(self) -> int:
        """Count total segments"""
        async with get_session() as session:
            result = await session.execute(select(func.count(SegmentModel.id)))
            return result.scalar() or 0
