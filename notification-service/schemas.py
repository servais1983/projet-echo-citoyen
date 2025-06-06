from pydantic import BaseModel, EmailStr
from typing import Optional, Dict
from datetime import datetime
from models import NotificationChannel, NotificationPriority

class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    is_active: bool
    is_admin: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True

class NotificationBase(BaseModel):
    title: str
    content: str
    channel: NotificationChannel
    recipient: str
    priority: NotificationPriority

class NotificationCreate(NotificationBase):
    pass

class NotificationResponse(NotificationBase):
    id: int
    status: str
    created_at: datetime
    sent_at: Optional[datetime] = None
    created_by: int

    class Config:
        orm_mode = True

class NotificationStats(BaseModel):
    total_notifications: int
    notifications_by_channel: Dict[str, int]
    notifications_by_priority: Dict[str, int]

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None
    is_admin: bool = False 