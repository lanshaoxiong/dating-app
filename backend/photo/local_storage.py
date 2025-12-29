"""Local filesystem storage implementation

This implementation stores files on the local filesystem.
Suitable for development and testing.

For production, use S3Storage, GCSStorage, or R2Storage instead.
"""

import os
import uuid
import aiofiles
from pathlib import Path
from typing import BinaryIO

from photo.storage_interface import StorageService


class LocalStorage(StorageService):
    """Local filesystem storage implementation"""
    
    # Allowed file types (MIME types)
    ALLOWED_TYPES = {
        'image/jpeg',
        'image/png',
        'image/webp',
    }
    
    # Maximum file size (10MB)
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB in bytes
    
    def __init__(self, upload_dir: str = "uploads/photos"):
        """Initialize local storage
        
        Args:
            upload_dir: Directory to store uploaded files
        """
        self.upload_dir = Path(upload_dir)
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        
        # Base URL for accessing files
        # In production, this would be your domain
        self.base_url = os.getenv("BASE_URL", "http://localhost:8000")
    
    def validate_file(self, filename: str, content_type: str, file_size: int) -> None:
        """Validate file before upload
        
        Args:
            filename: Original filename
            content_type: MIME type
            file_size: File size in bytes
            
        Raises:
            ValueError: If file is invalid
        """
        # Validate content type
        if content_type not in self.ALLOWED_TYPES:
            raise ValueError(
                f"Invalid file type: {content_type}. "
                f"Allowed types: {', '.join(self.ALLOWED_TYPES)}"
            )
        
        # Validate file size
        if file_size > self.MAX_FILE_SIZE:
            max_mb = self.MAX_FILE_SIZE / (1024 * 1024)
            actual_mb = file_size / (1024 * 1024)
            raise ValueError(
                f"File too large: {actual_mb:.2f}MB. "
                f"Maximum size: {max_mb:.0f}MB"
            )
        
        # Validate filename extension
        ext = Path(filename).suffix.lower()
        valid_extensions = {'.jpg', '.jpeg', '.png', '.webp'}
        if ext not in valid_extensions:
            raise ValueError(
                f"Invalid file extension: {ext}. "
                f"Allowed extensions: {', '.join(valid_extensions)}"
            )
    
    async def upload(self, file: BinaryIO, filename: str, content_type: str) -> str:
        """Upload file to local filesystem
        
        Args:
            file: File binary data
            filename: Original filename
            content_type: MIME type
            
        Returns:
            URL to access the uploaded file
        """
        # Generate unique filename to avoid collisions
        ext = Path(filename).suffix.lower()
        unique_filename = f"{uuid.uuid4()}{ext}"
        file_path = self.upload_dir / unique_filename
        
        # Write file asynchronously
        async with aiofiles.open(file_path, 'wb') as f:
            content = await file.read()
            await f.write(content)
        
        # Return URL
        return f"{self.base_url}/uploads/photos/{unique_filename}"
    
    async def delete(self, file_url: str) -> None:
        """Delete file from local filesystem
        
        Args:
            file_url: URL of the file to delete
        """
        # Extract filename from URL
        # URL format: http://localhost:8000/uploads/photos/uuid.jpg
        filename = Path(file_url).name
        file_path = self.upload_dir / filename
        
        # Delete file if it exists
        if file_path.exists():
            file_path.unlink()
    
    async def get_signed_url(self, file_url: str, expires_in: int = 3600) -> str:
        """Get URL for file access
        
        For local storage, this just returns the same URL since files are publicly accessible.
        For cloud storage (S3, GCS), this would return a pre-signed URL.
        
        Args:
            file_url: URL of the file
            expires_in: URL expiration time in seconds (ignored for local storage)
            
        Returns:
            File URL (same as input for local storage)
        """
        return file_url
