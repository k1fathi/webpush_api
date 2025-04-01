from pydantic import BaseModel, EmailStr, validator
from typing import Optional, List, Dict
from datetime import date, datetime

class UserBase(BaseModel):
    name: str
    email: EmailStr
    birthday: Optional[date] = None

class UserCreate(UserBase):
    password: str
    role_ids: Optional[List[int]] = []
    segment_ids: Optional[List[int]] = []

class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    birthday: Optional[date] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None
    role_ids: Optional[List[int]] = None
    segment_ids: Optional[List[int]] = None

class UserInDB(UserBase):
    user_id: int
    is_active: bool
    last_login: Optional[datetime]
    membership_date: date
    permissions: List[str]

    class Config:
        orm_mode = True

class UserResponse(UserInDB):
    segments: List[str] = []
    roles: List[str] = []
