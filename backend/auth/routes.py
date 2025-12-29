"""FastAPI routes for authentication

ARCHITECTURE NOTE:
This app uses a HYBRID API approach:

1. REST (this file) - Used for:
   - Authentication endpoints (register, login) - Standard, widely understood
   - File uploads (photos) - multipart/form-data works better with REST
   
2. GraphQL (Task 14) - Used for:
   - Profile queries (getProfile, getMatches, getRecommendations)
   - Profile mutations (updateProfile, likeProfile, sendMessage)
   - Flexible data fetching for mobile apps
   
3. WebSocket (Task 12) - Used for:
   - Real-time chat messaging
   
WHY KEEP AUTH AS REST?
- Standard auth flow (POST /login, get token, use in Authorization header)
- Works seamlessly with both REST and GraphQL endpoints
- Widely understood by frontend developers
- JWT tokens work with any API style

The AuthService is API-agnostic and can be called from REST, GraphQL, or anywhere!
"""

from fastapi import APIRouter, Depends, HTTPException, status

from auth.auth_service import AuthService
from auth.schemas import (
    RegisterRequest,
    LoginRequest,
    AuthToken,
    UserResponse,
    PasswordResetRequest,
)
from auth.dependencies import get_auth_service, get_current_user
from auth.exceptions import (
    InvalidCredentialsError,
    UserAlreadyExistsError,
    UserNotFoundError,
)
from db.models.user import User


router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    request: RegisterRequest,
    auth_service: AuthService = Depends(get_auth_service),
):
    """Register a new user
    
    REST endpoint for user registration. This stays as REST (not GraphQL) because:
    - Standard authentication pattern
    - Works with any frontend framework
    - Simple, well-understood flow
    
    Args:
        request: Registration request with email and password
        auth_service: Authentication service
        
    Returns:
        UserResponse with created user data
        
    Raises:
        HTTPException 409: If email is already registered
    """
    try:
        user = await auth_service.register(request.email, request.password)
        return user
    except UserAlreadyExistsError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        )


@router.post("/login", response_model=AuthToken)
async def login(
    request: LoginRequest,
    auth_service: AuthService = Depends(get_auth_service),
):
    """Login user and return JWT token
    
    REST endpoint for authentication. Returns JWT token that works with:
    - REST endpoints (Authorization: Bearer <token>)
    - GraphQL endpoints (same Authorization header)
    - WebSocket connections (token in connection params)
    
    Args:
        request: Login request with email and password
        auth_service: Authentication service
        
    Returns:
        AuthToken with JWT access token
        
    Raises:
        HTTPException 401: If credentials are invalid
    """
    try:
        token = await auth_service.login(request.email, request.password)
        return token
    except InvalidCredentialsError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user),
):
    """Get current authenticated user information
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        UserResponse with user data
    """
    return UserResponse.model_validate(current_user)


@router.post("/password-reset/request", status_code=status.HTTP_204_NO_CONTENT)
async def request_password_reset(
    request: PasswordResetRequest,
    auth_service: AuthService = Depends(get_auth_service),
):
    """Request password reset email
    
    Args:
        request: Password reset request with email
        auth_service: Authentication service
        
    Raises:
        HTTPException 404: If user not found
        
    Note:
        Returns 204 even if user doesn't exist (security best practice)
    """
    try:
        await auth_service.request_password_reset(request.email)
    except UserNotFoundError:
        # Don't reveal if user exists (security best practice)
        pass
    
    return None
