"""Pydantic schemas for authentication"""

from datetime import datetime
from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    """User registration request"""
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100)


class LoginRequest(BaseModel):
    """User login request"""
    email: EmailStr
    password: str


class AuthToken(BaseModel):
    """Authentication token response"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds


class UserResponse(BaseModel):
    """User response (without sensitive data)"""
    id: str
    email: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class PasswordResetRequest(BaseModel):
    """Password reset request"""
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    """Password reset confirmation"""
    token: str
    new_password: str = Field(..., min_length=8, max_length=100)
