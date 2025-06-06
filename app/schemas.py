from pydantic import BaseModel, EmailStr, HttpUrl, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from .models import NotificationStatus, NotificationChannel, NotificationPriority
import re

class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    username: EmailStr
    password: str

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None

class User(UserBase):
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
    type: str = "info"
    status: str = "pending"
    template_id: Optional[int] = None
    notification_metadata: Optional[Dict[str, Any]] = None

    @validator('title', 'content')
    def sanitize_input(cls, v):
        # Supprime les balises HTML et les caractères spéciaux
        v = re.sub(r'<[^>]*>', '', v)
        v = re.sub(r'[;\\\'"]', '', v)
        return v

    @validator('type')
    def validate_type(cls, v):
        if v not in ['info', 'warning', 'error', 'success']:
            raise ValueError('Invalid type value')
        return v

    @validator('status')
    def validate_status(cls, v):
        if v not in ['pending', 'sent', 'delivered', 'failed']:
            raise ValueError('Invalid status value')
        return v

class NotificationCreate(NotificationBase):
    pass

class NotificationUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    type: Optional[str] = None
    status: Optional[str] = None
    user_id: Optional[int] = None
    template_id: Optional[int] = None
    meta_data: Optional[Dict[str, Any]] = None

class Notification(NotificationBase):
    id: int
    status: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    sent_at: Optional[datetime] = None

    class Config:
        orm_mode = True

class TemplateBase(BaseModel):
    name: str
    content: str
    channel: str
    meta_data: Dict[str, Any]

class TemplateCreate(TemplateBase):
    pass

class TemplateUpdate(BaseModel):
    name: Optional[str] = None
    content: Optional[str] = None
    channel: Optional[str] = None
    meta_data: Optional[Dict[str, Any]] = None

class Template(TemplateBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True

class WebhookBase(BaseModel):
    url: str
    events: List[str]
    is_active: bool = True
    meta_data: Optional[Dict[str, Any]] = None

class WebhookCreate(WebhookBase):
    pass

class WebhookUpdate(BaseModel):
    url: Optional[str] = None
    events: Optional[List[str]] = None
    is_active: Optional[bool] = None
    meta_data: Optional[Dict[str, Any]] = None

class Webhook(WebhookBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None 