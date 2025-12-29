"""Profile service implementation"""

import uuid
from typing import Optional
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from geoalchemy2.elements import WKTElement

from db.models.profile import Profile, Photo, Prompt, UserPreferences
from profile.schemas import (
    ProfileInput,
    ProfileUpdate,
    ProfileResponse,
    PromptInput,
    Coordinates,
)
from profile.exceptions import (
    ProfileNotFoundError,
    ProfileAlreadyExistsError,
    InvalidPhotoCountError,
)


class ProfileService:
    """Service for handling profile management"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_profile(self, user_id: str, data: ProfileInput) -> ProfileResponse:
        """Create a new profile for a user
        
        Args:
            user_id: User ID
            data: Profile input data
            
        Returns:
            ProfileResponse with created profile
            
        Raises:
            ProfileAlreadyExistsError: If user already has a profile
        """
        # Check if profile already exists
        result = await self.db.execute(
            select(Profile).where(Profile.user_id == user_id)
        )
        existing_profile = result.scalar_one_or_none()
        
        if existing_profile:
            raise ProfileAlreadyExistsError(f"User {user_id} already has a profile")
        
        # Create profile
        profile = Profile(
            id=str(uuid.uuid4()),
            user_id=user_id,
            name=data.name,
            age=data.age,
            bio=data.bio,
        )
        
        # Set location if provided
        if data.location:
            profile.location = self._coordinates_to_wkt(data.location)
        
        self.db.add(profile)
        await self.db.flush()  # Flush to get profile.id for relationships
        
        # Create prompts
        for prompt_data in data.prompts:
            prompt = Prompt(
                id=str(uuid.uuid4()),
                profile_id=profile.id,
                question=prompt_data.question,
                answer=prompt_data.answer,
                order=prompt_data.order,
            )
            self.db.add(prompt)
        
        # Create preferences
        if data.preferences:
            preferences = UserPreferences(
                id=str(uuid.uuid4()),
                profile_id=profile.id,
                min_age=data.preferences.min_age,
                max_age=data.preferences.max_age,
                max_distance=data.preferences.max_distance,
                activity_level=data.preferences.activity_level,
                distance_unit=data.preferences.distance_unit,
            )
            self.db.add(preferences)
        
        await self.db.commit()
        
        # Reload profile with relationships
        return await self.get_profile(user_id)
    
    async def update_profile(self, user_id: str, data: ProfileUpdate) -> ProfileResponse:
        """Update an existing profile
        
        Args:
            user_id: User ID
            data: Profile update data
            
        Returns:
            ProfileResponse with updated profile
            
        Raises:
            ProfileNotFoundError: If profile doesn't exist
        """
        # Get existing profile
        result = await self.db.execute(
            select(Profile)
            .where(Profile.user_id == user_id)
            .options(
                selectinload(Profile.prompts),
                selectinload(Profile.preferences)
            )
        )
        profile = result.scalar_one_or_none()
        
        if not profile:
            raise ProfileNotFoundError(f"Profile for user {user_id} not found")
        
        # Update basic fields
        if data.name is not None:
            profile.name = data.name
        if data.age is not None:
            profile.age = data.age
        if data.bio is not None:
            profile.bio = data.bio
        if data.location is not None:
            profile.location = self._coordinates_to_wkt(data.location)
        
        # Update prompts if provided
        if data.prompts is not None:
            # Delete existing prompts
            await self.db.execute(
                delete(Prompt).where(Prompt.profile_id == profile.id)
            )
            
            # Create new prompts
            for prompt_data in data.prompts:
                prompt = Prompt(
                    id=str(uuid.uuid4()),
                    profile_id=profile.id,
                    question=prompt_data.question,
                    answer=prompt_data.answer,
                    order=prompt_data.order,
                )
                self.db.add(prompt)
        
        # Update preferences if provided
        if data.preferences is not None:
            if profile.preferences:
                # Update existing preferences
                profile.preferences.min_age = data.preferences.min_age
                profile.preferences.max_age = data.preferences.max_age
                profile.preferences.max_distance = data.preferences.max_distance
                profile.preferences.activity_level = data.preferences.activity_level
                profile.preferences.distance_unit = data.preferences.distance_unit
            else:
                # Create new preferences
                preferences = UserPreferences(
                    id=str(uuid.uuid4()),
                    profile_id=profile.id,
                    min_age=data.preferences.min_age,
                    max_age=data.preferences.max_age,
                    max_distance=data.preferences.max_distance,
                    activity_level=data.preferences.activity_level,
                    distance_unit=data.preferences.distance_unit,
                )
                self.db.add(preferences)
        
        await self.db.commit()
        
        # Reload profile with relationships
        return await self.get_profile(user_id)
    
    async def get_profile(self, user_id: str) -> ProfileResponse:
        """Get profile by user ID
        
        Args:
            user_id: User ID
            
        Returns:
            ProfileResponse with profile data
            
        Raises:
            ProfileNotFoundError: If profile doesn't exist
        """
        result = await self.db.execute(
            select(Profile)
            .where(Profile.user_id == user_id)
            .options(
                selectinload(Profile.photos),
                selectinload(Profile.prompts),
                selectinload(Profile.preferences)
            )
        )
        profile = result.scalar_one_or_none()
        
        if not profile:
            raise ProfileNotFoundError(f"Profile for user {user_id} not found")
        
        return self._profile_to_response(profile)
    
    async def delete_profile(self, user_id: str) -> None:
        """Delete profile and all associated data (cascade deletion)
        
        Args:
            user_id: User ID
            
        Raises:
            ProfileNotFoundError: If profile doesn't exist
        """
        result = await self.db.execute(
            select(Profile).where(Profile.user_id == user_id)
        )
        profile = result.scalar_one_or_none()
        
        if not profile:
            raise ProfileNotFoundError(f"Profile for user {user_id} not found")
        
        # Delete profile (cascade will handle photos, prompts, preferences)
        await self.db.delete(profile)
        await self.db.commit()
    
    async def add_prompt(self, user_id: str, prompt_data: PromptInput) -> ProfileResponse:
        """Add a prompt to a profile
        
        Args:
            user_id: User ID
            prompt_data: Prompt input data
            
        Returns:
            ProfileResponse with updated profile
            
        Raises:
            ProfileNotFoundError: If profile doesn't exist
        """
        result = await self.db.execute(
            select(Profile).where(Profile.user_id == user_id)
        )
        profile = result.scalar_one_or_none()
        
        if not profile:
            raise ProfileNotFoundError(f"Profile for user {user_id} not found")
        
        # Create new prompt
        prompt = Prompt(
            id=str(uuid.uuid4()),
            profile_id=profile.id,
            question=prompt_data.question,
            answer=prompt_data.answer,
            order=prompt_data.order,
        )
        self.db.add(prompt)
        await self.db.commit()
        
        return await self.get_profile(user_id)
    
    async def update_prompt(
        self, user_id: str, prompt_id: str, prompt_data: PromptInput
    ) -> ProfileResponse:
        """Update a prompt
        
        Args:
            user_id: User ID
            prompt_id: Prompt ID
            prompt_data: Updated prompt data
            
        Returns:
            ProfileResponse with updated profile
            
        Raises:
            ProfileNotFoundError: If profile or prompt doesn't exist
        """
        # Get profile to verify ownership
        result = await self.db.execute(
            select(Profile).where(Profile.user_id == user_id)
        )
        profile = result.scalar_one_or_none()
        
        if not profile:
            raise ProfileNotFoundError(f"Profile for user {user_id} not found")
        
        # Get prompt
        result = await self.db.execute(
            select(Prompt).where(
                Prompt.id == prompt_id,
                Prompt.profile_id == profile.id
            )
        )
        prompt = result.scalar_one_or_none()
        
        if not prompt:
            raise ProfileNotFoundError(f"Prompt {prompt_id} not found")
        
        # Update prompt
        prompt.question = prompt_data.question
        prompt.answer = prompt_data.answer
        prompt.order = prompt_data.order
        
        await self.db.commit()
        
        return await self.get_profile(user_id)
    
    async def delete_prompt(self, user_id: str, prompt_id: str) -> ProfileResponse:
        """Delete a prompt
        
        Args:
            user_id: User ID
            prompt_id: Prompt ID
            
        Returns:
            ProfileResponse with updated profile
            
        Raises:
            ProfileNotFoundError: If profile or prompt doesn't exist
        """
        # Get profile to verify ownership
        result = await self.db.execute(
            select(Profile).where(Profile.user_id == user_id)
        )
        profile = result.scalar_one_or_none()
        
        if not profile:
            raise ProfileNotFoundError(f"Profile for user {user_id} not found")
        
        # Get prompt
        result = await self.db.execute(
            select(Prompt).where(
                Prompt.id == prompt_id,
                Prompt.profile_id == profile.id
            )
        )
        prompt = result.scalar_one_or_none()
        
        if not prompt:
            raise ProfileNotFoundError(f"Prompt {prompt_id} not found")
        
        # Delete prompt
        await self.db.delete(prompt)
        await self.db.commit()
        
        return await self.get_profile(user_id)
    
    def _coordinates_to_wkt(self, coords: Coordinates) -> WKTElement:
        """Convert Coordinates to PostGIS WKT format
        
        Args:
            coords: Coordinates object
            
        Returns:
            WKTElement for PostGIS
        """
        return WKTElement(
            f'POINT({coords.longitude} {coords.latitude})',
            srid=4326
        )
    
    def _wkt_to_coordinates(self, wkt: str) -> Optional[Coordinates]:
        """Convert PostGIS WKT to Coordinates
        
        Args:
            wkt: WKT string from database
            
        Returns:
            Coordinates object or None
        """
        if not wkt:
            return None
        
        # Parse WKT format: "POINT(longitude latitude)"
        # Note: PostGIS stores as (lon, lat) but we return as (lat, lon)
        try:
            # Remove "POINT(" and ")"
            coords_str = wkt.replace('POINT(', '').replace(')', '')
            lon, lat = map(float, coords_str.split())
            return Coordinates(latitude=lat, longitude=lon)
        except (ValueError, AttributeError):
            return None
    
    def _profile_to_response(self, profile: Profile) -> ProfileResponse:
        """Convert Profile model to ProfileResponse
        
        Args:
            profile: Profile model instance
            
        Returns:
            ProfileResponse
        """
        # Convert location from WKT to Coordinates
        location = None
        if profile.location:
            # Use geoalchemy2 to get WKT string
            from geoalchemy2.shape import to_shape
            point = to_shape(profile.location)
            location = Coordinates(latitude=point.y, longitude=point.x)
        
        return ProfileResponse(
            id=profile.id,
            user_id=profile.user_id,
            name=profile.name,
            age=profile.age,
            bio=profile.bio,
            location=location,
            photos=[],  # Photos will be populated by photo service
            prompts=[p for p in profile.prompts] if profile.prompts else [],
            preferences=profile.preferences if profile.preferences else None,
            created_at=profile.created_at,
            updated_at=profile.updated_at,
        )
