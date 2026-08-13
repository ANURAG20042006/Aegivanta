from typing import Literal, Optional
from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    """Payload for user authentication."""
    username: str = Field(..., json_schema_extra={"example": "analyst_admin"})
    password: str = Field(..., json_schema_extra={"example": "SecurePassword123!"})


class RegisterRequest(BaseModel):
    """Payload for registering a new user."""
    username: str = Field(..., min_length=3, max_length=50, json_schema_extra={"example": "cyber_analyst"})
    email: EmailStr = Field(..., json_schema_extra={"example": "analyst@sentinelai.io"})
    password: str = Field(..., min_length=6, json_schema_extra={"example": "SecurePass123!"})
    full_name: str = Field(..., json_schema_extra={"example": "Jane Doe"})
    role: Literal["analyst", "viewer"] = Field(default="analyst", json_schema_extra={"example": "analyst"})


class Token(BaseModel):
    """JWT Token response schema."""
    access_token: str
    token_type: str = "bearer"
    expires_in_minutes: int
    user_id: str
    username: str
    role: str


class TokenData(BaseModel):
    """Decoded JWT payload data."""
    sub: Optional[str] = None
    role: Optional[str] = None
