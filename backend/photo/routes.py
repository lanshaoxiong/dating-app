"""FastAPI routes for photo management

ARCHITECTURE NOTE:
Photo uploads use REST (not GraphQL) because:
- multipart/form-data works better with REST
- File uploads are binary operations, not data queries
- Standard pattern for file uploads across all frameworks

The PhotoService is API-agnostic and can be called from anywhere!
"""

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession

from photo.photo_service import PhotoService
from photo.schemas import (
    PhotoResponse,
    PhotoUploadResponse,
    PhotoReorderRequest,
    PhotoReorderResponse,
)
from photo.exceptions import (
    PhotoNotFoundError,
    InvalidPhotoCountError,
    ProfileNotFoundError,
)
from photo.local_storage import LocalStorage
from db.database import get_db
from auth.dependencies import get_current_user
from db.models.user import User


router = APIRouter(prefix="/photos", tags=["photos"])


def get_photo_service(db: AsyncSession = Depends(get_db)) -> PhotoService:
    """Dependency for getting photo service
    
    Returns:
        PhotoService with local storage
        
    Note:
        In production, swap LocalStorage for S3Storage, GCSStorage, etc.
        by changing the storage parameter.
    """
    storage = LocalStorage()
    return PhotoService(db, storage)


@router.post("/upload", response_model=PhotoUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_photo(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    photo_service: PhotoService = Depends(get_photo_service),
):
    """Upload a photo to user's profile
    
    REST endpoint for file upload. Uses multipart/form-data which works
    better with REST than GraphQL.
    
    Args:
        file: Uploaded file (JPEG, PNG, or WebP, max 10MB)
        current_user: Authenticated user
        photo_service: Photo service
        
    Returns:
        PhotoUploadResponse with uploaded photo data
        
    Raises:
        HTTPException 404: If profile doesn't exist
        HTTPException 400: If file validation fails or max photos reached
    """
    try:
        # Get file info
        content = await file.read()
        file_size = len(content)
        
        # Reset file pointer for service to read
        await file.seek(0)
        
        # Upload photo
        photo = await photo_service.upload_photo(
            user_id=current_user.id,
            file=file.file,
            filename=file.filename,
            content_type=file.content_type,
            file_size=file_size,
        )
        
        return PhotoUploadResponse(
            photo=PhotoResponse.model_validate(photo),
            message="Photo uploaded successfully"
        )
        
    except ProfileNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except (InvalidPhotoCountError, ValueError) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.delete("/{photo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_photo(
    photo_id: str,
    current_user: User = Depends(get_current_user),
    photo_service: PhotoService = Depends(get_photo_service),
):
    """Delete a photo from user's profile
    
    Args:
        photo_id: Photo ID to delete
        current_user: Authenticated user
        photo_service: Photo service
        
    Raises:
        HTTPException 404: If profile or photo doesn't exist
        HTTPException 400: If deleting would leave less than 2 photos
    """
    try:
        await photo_service.delete_photo(current_user.id, photo_id)
        return None
        
    except ProfileNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except PhotoNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except InvalidPhotoCountError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.put("/reorder", response_model=PhotoReorderResponse)
async def reorder_photos(
    request: PhotoReorderRequest,
    current_user: User = Depends(get_current_user),
    photo_service: PhotoService = Depends(get_photo_service),
):
    """Reorder photos in user's profile
    
    Args:
        request: List of photo IDs in desired order
        current_user: Authenticated user
        photo_service: Photo service
        
    Returns:
        PhotoReorderResponse with reordered photos
        
    Raises:
        HTTPException 404: If profile doesn't exist
        HTTPException 400: If photo IDs don't match existing photos
    """
    try:
        photos = await photo_service.reorder_photos(
            current_user.id,
            request.photo_ids
        )
        
        return PhotoReorderResponse(
            photos=[PhotoResponse.model_validate(p) for p in photos],
            message="Photos reordered successfully"
        )
        
    except ProfileNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("/", response_model=list[PhotoResponse])
async def get_photos(
    current_user: User = Depends(get_current_user),
    photo_service: PhotoService = Depends(get_photo_service),
):
    """Get all photos for user's profile
    
    Args:
        current_user: Authenticated user
        photo_service: Photo service
        
    Returns:
        List of photos ordered by order field
        
    Raises:
        HTTPException 404: If profile doesn't exist
    """
    try:
        photos = await photo_service.get_photos(current_user.id)
        return [PhotoResponse.model_validate(p) for p in photos]
        
    except ProfileNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
