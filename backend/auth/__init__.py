"""Authentication module for PupMatch backend

This module provides user authentication services including:
- User registration
- Login with JWT tokens
- Token validation
- Password hashing with bcrypt
- Password reset flow
"""

from auth.service import AuthService
from auth.schemas import (
    RegisterRequest,
    LoginRequest,
    AuthToken,
    UserResponse,
    PasswordResetRequest,
    PasswordResetConfirm,
)
from auth.dependencies import get_current_user, require_auth

__all__ = [
    "AuthService",
    "RegisterRequest",
    "LoginRequest",
    "AuthToken",
    "UserResponse",
    "PasswordResetRequest",
    "PasswordResetConfirm",
    "get_current_user",
    "require_auth",
]
