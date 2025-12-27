"""FastAPI dependencies for authentication"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from db.database import get_db
from db.models.user import User
from auth.service import AuthService
from auth.exceptions import InvalidTokenError, UserNotFoundError


# HTTP Bearer token scheme
security = HTTPBearer()


async def get_auth_service(db: AsyncSession = Depends(get_db)) -> AuthService:
    """Get authentication service instance
    
    Args:
        db: Database session
        
    Returns:
        AuthService instance
    """
    return AuthService(db)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    auth_service: AuthService = Depends(get_auth_service),
) -> User:
    """Get current authenticated user from JWT token
    
    Args:
        credentials: HTTP Bearer credentials
        auth_service: Authentication service
        
    Returns:
        Current user
        
    Raises:
        HTTPException: If token is invalid or user not found
    """
    token = credentials.credentials
    
    try:
        user = await auth_service.validate_token(token)
        return user
    except (InvalidTokenError, UserNotFoundError) as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )


async def require_auth(
    current_user: User = Depends(get_current_user),
) -> User:
    """Require authentication (alias for get_current_user)
    
    This is a convenience dependency that makes the intent clearer
    when you just need to ensure the user is authenticated.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        Current user
    """
    return current_user
