from typing import Any, Dict, List, Optional
"""Domain exceptions - Business rule violations and domain errors."""


class CaptionGenerationError(Exception):
    """Base exception for caption generation domain errors."""
    
    pass


class InvalidProviderError(CaptionGenerationError):
    """Raised when an invalid or unavailable AI provider is requested."""
    
    def __init__(self, provider: str, available_providers: Optional[List[str]] = None):
        self.provider = provider
        self.available_providers = available_providers or []
        
        if self.available_providers:
            available_str = ", ".join(self.available_providers)
            message = f"Provider '{provider}' is invalid or unavailable. Available: {available_str}"
        else:
            message = f"Provider '{provider}' is invalid or unavailable"
        
        super().__init__(message)


class InvalidImageError(CaptionGenerationError):
    """Raised when image data is invalid or corrupted."""
    
    def __init__(self, reason: str):
        self.reason = reason
        super().__init__(f"Invalid image: {reason}")


class AIProviderUnavailableError(CaptionGenerationError):
    """Raised when AI provider service is unavailable."""
    
    def __init__(self, provider: str, reason: str):
        self.provider = provider
        self.reason = reason
        super().__init__(f"AI provider '{provider}' unavailable: {reason}")


class InvalidCaptionDataError(CaptionGenerationError):
    """Raised when AI provider returns invalid  caption data."""
    
    def __init__(self, reason: str, raw_data: Optional[str] = None):
        self.reason = reason
        self.raw_data = raw_data
        super().__init__(f"Invalid caption data: {reason}")
