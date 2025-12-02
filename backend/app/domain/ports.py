from typing import Any, Dict, List, Optional
"""Domain ports - Abstract interfaces for dependency inversion."""

from abc import ABC, abstractmethod
from typing import Protocol

from .entities import CaptionEntity


class AIProviderPort(ABC):
    """
    Abstract interface for AI caption generation providers.
    
    This port (interface) follows the Dependency Inversion Principle:
    - Domain defines the contract
    - Infrastructure implements the contract
    - Application depends on the port, not the implementation
    """
    
    @abstractmethod
    async def generate_caption(
        self,
        image_data: bytes,
        mime_type: str,
        context: Optional[str] = None,
    ) -> CaptionEntity:
        """
        Generate caption from image data.
        
        Args:
            image_data: Raw image bytes
            mime_type: MIME type of the image
            context: Optional context/tone for generation
            
        Returns:
            CaptionEntity with generated content
            
        Raises:
            InvalidImageError: If image is invalid
            AIProviderUnavailableError: If provider service is unavailable
            InvalidCaptionDataError: If provider returns invalid data
        """
        pass


class LoggerPort(Protocol):
    """
    Abstract interface for logging.
    
    Using Protocol instead of ABC for structural subtyping.
    Any class with these methods satisfies the interface.
    """
    
    def debug(self, message: str, **kwargs: any) -> None:
        """Log debug message."""
        ...
    
    def info(self, message: str, **kwargs: any) -> None:
        """Log info message."""
        ...
    
    def warning(self, message: str, **kwargs: any) -> None:
        """Log warning message."""
        ...
    
    def error(self, message: str, **kwargs: any) -> None:
        """Log error message."""
        ...
    
    def exception(self, message: str, **kwargs: any) -> None:
        """Log exception with stack trace."""
        ...
