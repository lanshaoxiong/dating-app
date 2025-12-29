"""Photo service implementation"""

import uuid
from typing import BinaryIO
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.models.profile import Photo, Profile
from photo.storage_interface import StorageService
from photo.exceptions import (
    PhotoNotFoundError,
    InvalidPhotoCountError,
    ProfileNotFoundError,
)


class PhotoService:
    """Service for handling photo management"""
    
    # Photo count constraints
    MIN_PHOTOS = 2
    MAX_PHOTOS = 6
    
    def __init__(self, db: AsyncSession, storage: StorageService):
        self.db = db
        self.storage = storage
    
    async def upload_photo(
        self,
        user_id: str,
        file: BinaryIO,
        filename: str,
        content_type: str,
        file_size: int
    ) -> Photo:
        """Upload a photo for a user's profile
        
        Args:
            user_id: User ID
            file: File binary data
            filename: Original filename
            content_type: MIME type
            file_size: File size in bytes
            
        Returns:
            Photo object with URL
            
        Raises:
            ProfileNotFoundError: If profile doesn't exist
            InvalidPhotoCountError: If profile already has 6 photos
            ValueError: If file validation fails
        """
        # Get profile
        result = await self.db.execute(
            select(Profile).where(Profile.user_id == user_id)
        )
        profile = result.scalar_one_or_none()
        
        if not profile:
            raise ProfileNotFoundError(f"Profile for user {user_id} not found")
        
        # Check photo count
        result = await self.db.execute(
            select(Photo).where(Photo.profile_id == profile.id)
        )
        existing_photos = result.scalars().all()
        
        if len(existing_photos) >= self.MAX_PHOTOS:
            raise InvalidPhotoCountError(
                f"Profile already has {self.MAX_PHOTOS} photos. "
                f"Delete a photo before uploading a new one."
            )
        
        # Validate file
        self.storage.validate_file(filename, content_type, file_size)
        
        # Upload to storage
        file_url = await self.storage.upload(file, filename, content_type)
        
        # Determine order (next available position)
        order = len(existing_photos)
        
        # Create photo record
        photo = Photo(
            id=str(uuid.uuid4()),
            profile_id=profile.id,
            url=file_url,
            order=order,
        )
        
        self.db.add(photo)
        await self.db.commit()
        await self.db.refresh(photo)
        
        return photo
    
    async def delete_photo(self, user_id: str, photo_id: str) -> None:
        """Delete a photo
        
        Args:
            user_id: User ID
            photo_id: Photo ID
            
        Raises:
            ProfileNotFoundError: If profile doesn't exist
            PhotoNotFoundError: If photo doesn't exist
            InvalidPhotoCountError: If deleting would leave less than 2 photos
        """
        # Get profile
        result = await self.db.execute(
            select(Profile).where(Profile.user_id == user_id)
        )
        profile = result.scalar_one_or_none()
        
        if not profile:
            raise ProfileNotFoundError(f"Profile for user {user_id} not found")
        
        # Get photo
        result = await self.db.execute(
            select(Photo).where(
                Photo.id == photo_id,
                Photo.profile_id == profile.id
            )
        )
        photo = result.scalar_one_or_none()
        
        if not photo:
            raise PhotoNotFoundError(f"Photo {photo_id} not found")
        
        # Check photo count (must have at least MIN_PHOTOS)
        result = await self.db.execute(
            select(Photo).where(Photo.profile_id == profile.id)
        )
        existing_photos = result.scalars().all()
        
        if len(existing_photos) <= self.MIN_PHOTOS:
            raise InvalidPhotoCountError(
                f"Cannot delete photo. Profile must have at least {self.MIN_PHOTOS} photos."
            )
        
        # Delete from storage
        await self.storage.delete(photo.url)
        
        # Delete from database
        await self.db.delete(photo)
        
        # Reorder remaining photos
        await self._reorder_photos_after_deletion(profile.id, photo.order)
        
        await self.db.commit()
    
    async def reorder_photos(self, user_id: str, photo_ids: list[str]) -> list[Photo]:
        """Reorder photos
        
        Args:
            user_id: User ID
            photo_ids: List of photo IDs in desired order
            
        Returns:
            List of photos in new order
            
        Raises:
            ProfileNotFoundError: If profile doesn't exist
            ValueError: If photo_ids don't match existing photos
        """
        # Get profile
        result = await self.db.execute(
            select(Profile).where(Profile.user_id == user_id)
        )
        profile = result.scalar_one_or_none()
        
        if not profile:
            raise ProfileNotFoundError(f"Profile for user {user_id} not found")
        
        # Get all photos for profile
        result = await self.db.execute(
            select(Photo).where(Photo.profile_id == profile.id)
        )
        existing_photos = {photo.id: photo for photo in result.scalars().all()}
        
        # Validate photo_ids
        if set(photo_ids) != set(existing_photos.keys()):
            raise ValueError(
                "photo_ids must match exactly with existing photos. "
                f"Expected {len(existing_photos)} photos, got {len(photo_ids)}"
            )
        
        # Update order
        for new_order, photo_id in enumerate(photo_ids):
            photo = existing_photos[photo_id]
            photo.order = new_order
        
        await self.db.commit()
        
        # Return photos in new order
        return [existing_photos[photo_id] for photo_id in photo_ids]
    
    async def get_photos(self, user_id: str) -> list[Photo]:
        """Get all photos for a user's profile
        
        Args:
            user_id: User ID
            
        Returns:
            List of photos ordered by order field
            
        Raises:
            ProfileNotFoundError: If profile doesn't exist
        """
        # Get profile
        result = await self.db.execute(
            select(Profile).where(Profile.user_id == user_id)
        )
        profile = result.scalar_one_or_none()
        
        if not profile:
            raise ProfileNotFoundError(f"Profile for user {user_id} not found")
        
        # Get photos
        result = await self.db.execute(
            select(Photo)
            .where(Photo.profile_id == profile.id)
            .order_by(Photo.order)
        )
        
        return list(result.scalars().all())
    
    async def _reorder_photos_after_deletion(self, profile_id: str, deleted_order: int) -> None:
        """Reorder photos after deletion to fill the gap
        
        Args:
            profile_id: Profile ID
            deleted_order: Order position of deleted photo
        """
        # Get photos with order > deleted_order
        result = await self.db.execute(
            select(Photo)
            .where(
                Photo.profile_id == profile_id,
                Photo.order > deleted_order
            )
        )
        
        # Decrement order for all photos after deleted one
        for photo in result.scalars().all():
            photo.order -= 1
