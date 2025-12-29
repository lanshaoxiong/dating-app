"""Profile-related exceptions"""


class ProfileNotFoundError(Exception):
    """Raised when profile is not found"""
    pass


class ProfileAlreadyExistsError(Exception):
    """Raised when user already has a profile"""
    pass


class InvalidPhotoCountError(Exception):
    """Raised when photo count constraints are violated"""
    pass
