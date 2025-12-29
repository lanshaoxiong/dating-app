"""Abstract storage interface for file management

This interface allows swapping between different storage providers
(local filesystem, AWS S3, Google Cloud Storage, Cloudflare R2, etc.)
without changing the application code.
"""

from abc import ABC, abstractmethod
from typing import BinaryIO


class StorageService(ABC):
    """Abstract storage service interface
    
    Implementations:
    - LocalStorage: Store files on local filesystem (development)
    - S3Storage: Store files on AWS S3 (production)
    - GCSStorage: Store files on Google Cloud Storage (production)
    - R2Storage: Store files on Cloudflare R2 (production)
    """
    
    @abstractmethod
    async def upload(self, file: BinaryIO, filename: str, content_type: str) -> str:
        """Upload file to storage
        
        Args:
            file: File binary data
            filename: Original filename
            content_type: MIME type (e.g., 'image/jpeg')
            
        Returns:
            URL to access the uploaded file
        """
        pass
    
    @abstractmethod
    async def delete(self, file_url: str) -> None:
        """Delete file from storage
        
        Args:
            file_url: URL of the file to delete
        """
        pass
    
    @abstractmethod
    async def get_signed_url(self, file_url: str, expires_in: int = 3600) -> str:
        """Get temporary signed URL for secure access
        
        Args:
            file_url: URL of the file
            expires_in: URL expiration time in seconds (default: 1 hour)
            
        Returns:
            Signed URL that expires after specified time
            
        Note:
            For local storage, this returns the same URL.
            For cloud storage (S3, GCS), this returns a pre-signed URL.
        """
        pass
    
    @abstractmethod
    def validate_file(self, filename: str, content_type: str, file_size: int) -> None:
        """Validate file before upload
        
        Args:
            filename: Original filename
            content_type: MIME type
            file_size: File size in bytes
            
        Raises:
            ValueError: If file is invalid (wrong type, too large, etc.)
        """
        pass
