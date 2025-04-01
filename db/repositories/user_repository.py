from sqlalchemy.orm import Session
from typing import List, Optional, Dict
from datetime import datetime
from db.models.user_model import User
from db.models.roles_model import Role
from db.models.segment_model import Segment

class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    async def create(self, user_data: Dict, role_ids: List[int] = None, segment_ids: List[int] = None) -> User:
        db_user = User(**{k: v for k, v in user_data.items() if hasattr(User, k)})
        
        if role_ids:
            roles = self.db.query(Role).filter(Role.id.in_(role_ids)).all()
            db_user.roles.extend(roles)
            
        if segment_ids:
            segments = self.db.query(Segment).filter(Segment.segment_id.in_(segment_ids)).all()
            db_user.segments.extend(segments)

        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return db_user

    async def get_by_email(self, email: str) -> Optional[User]:
        return self.db.query(User).filter(User.email == email).first()

    async def get_by_id(self, user_id: int) -> Optional[User]:
        return self.db.query(User).filter(User.user_id == user_id).first()

    async def get_users_by_segment(self, segment_id: int) -> List[User]:
        return self.db.query(User).join(User.segments).filter(Segment.segment_id == segment_id).all()

    async def update(self, user_id: int, user_data: Dict) -> Optional[User]:
        user = await self.get_by_id(user_id)
        if user:
            for key, value in user_data.items():
                if hasattr(user, key):
                    setattr(user, key, value)
            self.db.commit()
            self.db.refresh(user)
        return user

    async def update_last_login(self, user_id: int) -> bool:
        user = await self.get_by_id(user_id)
        if user:
            user.last_login = datetime.utcnow()
            self.db.commit()
            return True
        return False
