from typing import Any, Dict, List, Optional
"""Security utilities - Rate limiting, file validation, authentication."""

from fastapi import HTTPException, UploadFile
from slowapi import Limiter
from slowapi.util import get_remote_address

from .config import Settings


# Rate Limiter
def get_rate_limiter() -> Limiter:
    """
    Get rate limiter instance.
    
    Uses SlowAPI for FastAPI-compatible rate limiting.
    """
    return Limiter(key_func=get_remote_address)


# File Validation
class FileValidator:
    """Validates uploaded files for security."""
    
    def __init__(self, settings: Settings):
        """
        Initialize file validator.
        
        Args:
            settings: Application settings
        """
        self._max_size = settings.max_file_size_bytes
        self._allowed_types = {
            "image/jpeg",
            "image/jpg",
            "image/png",
            "image/webp",
            "image/gif",
        }
    
    async def validate(self, file: UploadFile) -> None:
        """
        Validate uploaded file.
        
        Args:
            file: Uploaded file
            
        Raises:
            HTTPException: If validation fails
        """
        # Validate content type
        if file.content_type not in self._allowed_types:
            allowed = ", ".join(sorted(self._allowed_types))
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file type: {file.content_type}. Allowed: {allowed}"
            )
        
        # Read file to check size
        contents = await file.read()
        file_size = len(contents)
        
        # Reset file pointer
        await file.seek(0)
        
        # Validate size
        if file_size > self._max_size:
            max_mb = self._max_size / (1024 * 1024)
            raise HTTPException(
                status_code=413,
                detail=f"File too large: {file_size / (1024 * 1024):.2f}MB. Maximum: {max_mb}MB"
            )
        
        if file_size == 0:
            raise HTTPException(
                status_code=400,
                detail="File is empty"
            )


# Authentication (scaffold for future implementation)
class AuthMiddleware:
    """
    Authentication middleware scaffold.
    
    Ready for implementation when authentication is needed.
    Currently disabled by default via settings.enable_auth.
    """
    
    def __init__(self, settings: Settings):
        """
        Initialize auth middleware.
        
        Args:
            settings: Application settings
        """
        self._enabled = settings.enable_auth
    
    def is_enabled(self) -> bool:
        """Check if authentication is enabled."""
        return self._enabled
    
    async def validate_token(self, token: str) -> Dict[str, Any]:
        """
        Validate JWT token (to be implemented).
        
        Args:
            token: JWT token
            
        Returns:
            User information from token
            
        Raises:
            HTTPException: If token is invalid
        """
        if not self._enabled:
            return {}
        
        # TODO: Implement JWT validation
        raise NotImplementedError("JWT validation not yet implemented")
    
    async def validate_api_key(self, api_key: str) -> Dict[str, Any]:
        """
        Validate API key (to be implemented).
        
        Args:
            api_key: API key
            
        Returns:
            User information from API key
            
        Raises:
            HTTPException: If API key is invalid
        """
        if not self._enabled:
            return {}
        
        # TODO: Implement API key validation
        raise NotImplementedError("API key validation not yet implemented")
