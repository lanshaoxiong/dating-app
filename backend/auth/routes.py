"""FastAPI routes for authentication"""

from fastapi import APIRouter, Depends, HTTPException, status

from auth.service import AuthService
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
