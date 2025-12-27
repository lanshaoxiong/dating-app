"""Custom exceptions for authentication"""


class AuthenticationError(Exception):
    """Base exception for authentication errors"""
    pass


class InvalidCredentialsError(AuthenticationError):
    """Raised when login credentials are invalid"""
    pass


class UserAlreadyExistsError(AuthenticationError):
    """Raised when trying to register with existing email"""
    pass


class InvalidTokenError(AuthenticationError):
    """Raised when JWT token is invalid or expired"""
    pass


class UserNotFoundError(AuthenticationError):
    """Raised when user is not found"""
    pass
