"""FastAPI dependencies for authentication"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from db.database import get_db
from db.models.user import User
from auth.auth_service import AuthService
from auth.exceptions import InvalidTokenError, UserNotFoundError


# HTTP Bearer token scheme
# This tells FastAPI to look for "Authorization: Bearer <token>" header
security = HTTPBearer()


async def get_auth_service(db: AsyncSession = Depends(get_db)) -> AuthService:
    """Get authentication service instance
    
    This is a dependency that creates an AuthService with a database session.
    FastAPI will automatically:
    1. Call get_db() to get a database session
    2. Pass it to AuthService constructor
    3. Return the AuthService instance
    
    Args:
        db: Database session (automatically injected by FastAPI)
        
    Returns:
        AuthService instance ready to use
    """
    return AuthService(db)


async def get_current_user(
    # Step 1: Extract Bearer token from Authorization header
    # Client sends: Authorization: Bearer eyJhbGci...
    # FastAPI extracts and creates HTTPAuthorizationCredentials object with:
    #   - scheme: "Bearer"
    #   - credentials: "eyJhbGci..." (the actual JWT token)
    credentials: HTTPAuthorizationCredentials = Depends(security),
    
    # Step 2: Get AuthService instance (with database session)
    auth_service: AuthService = Depends(get_auth_service),
) -> User:
    """Get current authenticated user from JWT token
    
    This dependency is used to protect endpoints that require authentication.
    It extracts the JWT token from the Authorization header, validates it,
    and returns the authenticated User object.
    
    Flow:
    1. Extract token from "Authorization: Bearer <token>" header
    2. Decode JWT and verify signature
    3. Check token expiration
    4. Get user from database
    5. Return User object to endpoint
    
    Args:
        credentials: HTTP Bearer credentials (contains JWT token)
        auth_service: Authentication service for token validation
        
    Returns:
        Current authenticated user
        
    Raises:
        HTTPException 401: If token is invalid, expired, or user not found
    """
    # Step 3: Extract the actual JWT token string
    # credentials.credentials = "eyJhbGci..." (the JWT token)
    # (Note: credentials.scheme = "Bearer")
    token = credentials.credentials
    
    try:
        # Step 4: Validate token and get user
        # This will:
        # - Decode JWT and verify signature
        # - Check expiration
        # - Query database for user
        user = await auth_service.validate_token(token)
        return user
    except (InvalidTokenError, UserNotFoundError) as e:
        # Step 5: If validation fails, return 401 Unauthorized
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
    
    Usage:
        @app.get("/protected")
        async def protected(user: User = Depends(require_auth)):
            # User is guaranteed to be authenticated here
            return {"user_id": user.id}
    
    Args:
        current_user: Current authenticated user (from get_current_user)
        
    Returns:
        Current authenticated user
        
    Raises:
        HTTPException 401: If not authenticated (via get_current_user)
    """
    return current_user
