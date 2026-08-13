from datetime import datetime
from typing import Literal, Optional
from pydantic import BaseModel, EmailStr, ConfigDict


class UserBase(BaseModel):
    """Base user schema."""
    username: str
    email: EmailStr
    full_name: str
    role: Literal["admin", "analyst", "viewer"]
    is_active: bool = True


class UserCreate(UserBase):
    """Schema for user creation by administrator."""
    password: str


class UserUpdate(BaseModel):
    """Schema for updating user details."""
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    role: Optional[Literal["admin", "analyst", "viewer"]] = None
    is_active: Optional[bool] = None
    password: Optional[str] = None


class UserResponse(UserBase):
    """Public user profile response schema."""
    id: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
