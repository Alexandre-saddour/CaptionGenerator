from typing import Any, Dict, List, Optional
"""Domain value objects - Immutable, self-validating domain concepts."""

from enum import Enum


class ProviderName(str, Enum):
    """AI provider identifiers."""
    
    GEMINI = "gemini"
    OPENAI = "openai"
    
    @classmethod
    def from_string(cls, value: str) -> "ProviderName":
        """
        Create ProviderName from string, case-insensitive.
        
        Args:
            value: Provider name string
            
        Returns:
            ProviderName enum value
            
        Raises:
            ValueError: If provider name is invalid
        """
        value_lower = value.lower().strip()
        try:
            return cls(value_lower)
        except ValueError:
            valid_providers = ", ".join([p.value for p in cls])
            raise ValueError(
                f"Invalid provider: '{value}'. Must be one of: {valid_providers}"
            )


class MimeType:
    """
    Value object for validated MIME types.
    
    Ensures only supported image MIME types are used.
    """
    
    SUPPORTED_TYPES = {
        "image/jpeg",
        "image/jpg",
        "image/png",
        "image/webp",
        "image/gif",
    }
    
    def __init__(self, value: str):
        """
        Create MimeType value object.
        
        Args:
            value: MIME type string
            
        Raises:
            ValueError: If MIME type is not supported
        """
        if value not in self.SUPPORTED_TYPES:
            supported = ", ".join(sorted(self.SUPPORTED_TYPES))
            raise ValueError(
                f"Unsupported MIME type: '{value}'. Supported types: {supported}"
            )
        self._value = value
    
    @property
    def value(self) -> str:
        """Get the MIME type string."""
        return self._value
    
    def __str__(self) -> str:
        return self._value
    
    def __repr__(self) -> str:
        return f"MimeType('{self._value}')"
    
    def __eq__(self, other: object) -> bool:
        if isinstance(other, MimeType):
            return self._value == other._value
        return False
    
    def __hash__(self) -> int:
        return hash(self._value)


class ImageContext:
    """
    Value object for image context/tone.
    
    Represents optional context or tone for caption generation.
    """
    
    def __init__(self, value: Optional[str] = None):
        """
        Create ImageContext value object.
        
        Args:
            value: Optional context string
        """
        if value is not None:
            # Strip and validate
            value = value.strip()
            if len(value) == 0:
                value = None
            elif len(value) > 500:
                raise ValueError("Context too long (maximum 500 characters)")
        
        self._value = value
    
    @property
    def value(self) -> Optional[str]:
        """Get the context string."""
        return self._value
    
    def has_context(self) -> bool:
        """Check if context is provided."""
        return self._value is not None
    
    def __str__(self) -> str:
        return self._value or ""
    
    def __repr__(self) -> str:
        return f"ImageContext({self._value!r})"
    
    def __eq__(self, other: object) -> bool:
        if isinstance(other, ImageContext):
            return self._value == other._value
        return False
