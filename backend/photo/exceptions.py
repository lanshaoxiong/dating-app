"""Photo-related exceptions"""


class PhotoNotFoundError(Exception):
    """Raised when photo is not found"""
    pass


class InvalidPhotoCountError(Exception):
    """Raised when photo count constraints are violated"""
    pass


class ProfileNotFoundError(Exception):
    """Raised when profile is not found"""
    pass
