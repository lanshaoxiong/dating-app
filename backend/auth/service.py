"""Authentication service implementation"""

import uuid
from datetime import datetime, timedelta
from typing import Optional

import bcrypt
from jose import JWTError, jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from db.models.user import User
from auth.schemas import AuthToken, UserResponse
from auth.exceptions import (
    InvalidCredentialsError,
    UserAlreadyExistsError,
    InvalidTokenError,
    UserNotFoundError,
)


class AuthService:
    """Service for handling user authentication"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def register(self, email: str, password: str) -> UserResponse:
        """Register a new user with email and password
        
        Args:
            email: User email address
            password: Plain text password (will be hashed)
            
        Returns:
            UserResponse with user data
            
        Raises:
            UserAlreadyExistsError: If email is already registered
        """
        # Check if user already exists
        result = await self.db.execute(
            select(User).where(User.email == email)
        )
        existing_user = result.scalar_one_or_none()
        
        if existing_user:
            raise UserAlreadyExistsError(f"User with email {email} already exists")
        
        # Hash password
        password_hash = self._hash_password(password)
        
        # Create new user
        user = User(
            id=str(uuid.uuid4()),
            email=email,
            password_hash=password_hash,
        )
        
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        
        return UserResponse.model_validate(user)
    
    async def login(self, email: str, password: str) -> AuthToken:
        """Login user and return JWT token
        
        Args:
            email: User email address
            password: Plain text password
            
        Returns:
            AuthToken with JWT access token
            
        Raises:
            InvalidCredentialsError: If email or password is incorrect
        """
        # Find user by email
        result = await self.db.execute(
            select(User).where(User.email == email)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            raise InvalidCredentialsError("Invalid email or password")
        
        # Verify password
        if not self._verify_password(password, user.password_hash):
            raise InvalidCredentialsError("Invalid email or password")
        
        # Generate JWT token
        token = self._create_access_token(user.id)
        
        return AuthToken(
            access_token=token,
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )
    
    async def validate_token(self, token: str) -> User:
        """Validate JWT token and return user
        
        Args:
            token: JWT access token
            
        Returns:
            User object
            
        Raises:
            InvalidTokenError: If token is invalid or expired
            UserNotFoundError: If user no longer exists
        """
        try:
            # Decode JWT token
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM]
            )
            user_id: str = payload.get("sub")
            
            if user_id is None:
                raise InvalidTokenError("Invalid token payload")
            
            # Check expiration
            exp = payload.get("exp")
            if exp and datetime.utcnow().timestamp() > exp:
                raise InvalidTokenError("Token has expired")
                
        except JWTError as e:
            raise InvalidTokenError(f"Invalid token: {str(e)}")
        
        # Get user from database
        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            raise UserNotFoundError(f"User {user_id} not found")
        
        return user
    
    async def request_password_reset(self, email: str) -> None:
        """Request password reset for user
        
        Args:
            email: User email address
            
        Raises:
            UserNotFoundError: If user doesn't exist
            
        Note:
            In production, this should send an email with reset link.
            For now, it just validates the user exists.
        """
        result = await self.db.execute(
            select(User).where(User.email == email)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            raise UserNotFoundError(f"User with email {email} not found")
        
        # TODO: Generate reset token and send email
        # For now, just validate user exists
        pass
    
    async def reset_password(self, token: str, new_password: str) -> None:
        """Reset user password with reset token
        
        Args:
            token: Password reset token
            new_password: New password (plain text, will be hashed)
            
        Raises:
            InvalidTokenError: If reset token is invalid
            UserNotFoundError: If user doesn't exist
            
        Note:
            This is a placeholder. Full implementation requires
            storing reset tokens in Redis with expiration.
        """
        # TODO: Implement password reset token validation
        # For now, this is a placeholder
        raise NotImplementedError("Password reset not yet implemented")
    
    def _hash_password(self, password: str) -> str:
        """Hash password using bcrypt
        
        Args:
            password: Plain text password
            
        Returns:
            Hashed password string
        """
        salt = bcrypt.gensalt(rounds=12)
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    def _verify_password(self, password: str, password_hash: str) -> bool:
        """Verify password against hash
        
        Args:
            password: Plain text password
            password_hash: Hashed password from database
            
        Returns:
            True if password matches, False otherwise
        """
        return bcrypt.checkpw(
            password.encode('utf-8'),
            password_hash.encode('utf-8')
        )
    
    def _create_access_token(self, user_id: str) -> str:
        """Create JWT access token
        
        Args:
            user_id: User ID to encode in token
            
        Returns:
            JWT token string
        """
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
        
        payload = {
            "sub": user_id,
            "exp": expire,
            "iat": datetime.utcnow(),
        }
        
        token = jwt.encode(
            payload,
            settings.SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM
        )
        
        return token
