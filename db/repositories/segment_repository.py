from db.models.user_model import User
from .base_repository import BaseRepository
from db.models.segment_model import Segment
from typing import List

class SegmentRepository(BaseRepository[Segment]):
    async def add_user_to_segment(self, segment_id: int, user_id: int) -> bool:
        segment = await self.get(segment_id)
        if segment:
            user = self.db.query(User).get(user_id)
            if user:
                segment.users.append(user)
                self.db.commit()
                return True
        return False

    async def get_segment_users(self, segment_id: int) -> List[User]:
        segment = await self.get(segment_id)
        return segment.users if segment else []

    async def remove_user_from_segment(self, segment_id: int, user_id: int) -> bool:
        segment = await self.get(segment_id)
        if segment:
            user = self.db.query(User).get(user_id)
            if user in segment.users:
                segment.users.remove(user)
                self.db.commit()
                return True
        return False
