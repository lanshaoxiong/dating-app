"""Pydantic schemas for photo management"""

from datetime import datetime
from pydantic import BaseModel, Field


class PhotoResponse(BaseModel):
    """Response schema for a photo"""
    id: str
    profile_id: str
    url: str
    order: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class PhotoUploadResponse(BaseModel):
    """Response schema for photo upload"""
    photo: PhotoResponse
    message: str = "Photo uploaded successfully"


class PhotoReorderRequest(BaseModel):
    """Request schema for reordering photos"""
    photo_ids: list[str] = Field(..., min_length=2, max_length=6)


class PhotoReorderResponse(BaseModel):
    """Response schema for photo reorder"""
    photos: list[PhotoResponse]
    message: str = "Photos reordered successfully"
