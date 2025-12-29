"""Pydantic schemas for profile management"""

from datetime import datetime
from typing import Optional, Literal
from pydantic import BaseModel, Field, field_validator


ActivityLevel = Literal['low', 'medium', 'high']
DistanceUnit = Literal['miles', 'kilometers']


class Coordinates(BaseModel):
    """Geographic coordinates"""
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)


class PromptInput(BaseModel):
    """Input schema for creating/updating a prompt"""
    question: str = Field(..., min_length=1, max_length=500)
    answer: str = Field(..., min_length=1, max_length=1000)
    order: int = Field(..., ge=0)


class PromptResponse(BaseModel):
    """Response schema for a prompt"""
    id: str
    profile_id: str
    question: str
    answer: str
    order: int
    
    class Config:
        from_attributes = True


class PhotoResponse(BaseModel):
    """Response schema for a photo"""
    id: str
    profile_id: str
    url: str
    order: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class UserPreferencesInput(BaseModel):
    """Input schema for user preferences"""
    min_age: int = Field(default=0, ge=0, le=20)
    max_age: int = Field(default=20, ge=0, le=20)
    max_distance: float = Field(default=25.0, gt=0)
    activity_level: ActivityLevel = Field(default='medium')
    distance_unit: DistanceUnit = Field(default='miles')
    
    @field_validator('max_age')
    @classmethod
    def validate_age_range(cls, v: int, info) -> int:
        """Ensure max_age >= min_age"""
        if 'min_age' in info.data and v < info.data['min_age']:
            raise ValueError('max_age must be greater than or equal to min_age')
        return v


class UserPreferencesResponse(BaseModel):
    """Response schema for user preferences"""
    id: str
    profile_id: str
    min_age: int
    max_age: int
    max_distance: float
    activity_level: ActivityLevel
    distance_unit: DistanceUnit
    
    class Config:
        from_attributes = True


class ProfileInput(BaseModel):
    """Input schema for creating a profile"""
    name: str = Field(..., min_length=1, max_length=100)
    age: int = Field(..., ge=0, le=20)
    bio: str = Field(..., min_length=1, max_length=2000)
    location: Optional[Coordinates] = None
    prompts: list[PromptInput] = Field(default_factory=list)
    preferences: Optional[UserPreferencesInput] = None


class ProfileUpdate(BaseModel):
    """Input schema for updating a profile"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    age: Optional[int] = Field(None, ge=0, le=20)
    bio: Optional[str] = Field(None, min_length=1, max_length=2000)
    location: Optional[Coordinates] = None
    prompts: Optional[list[PromptInput]] = None
    preferences: Optional[UserPreferencesInput] = None


class ProfileResponse(BaseModel):
    """Response schema for a profile with nested photos and prompts"""
    id: str
    user_id: str
    name: str
    age: int
    bio: str
    location: Optional[Coordinates] = None
    photos: list[PhotoResponse] = Field(default_factory=list)
    prompts: list[PromptResponse] = Field(default_factory=list)
    preferences: Optional[UserPreferencesResponse] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
