"""Domain entities - Pure business objects with no external dependencies."""

from dataclasses import dataclass
from typing import Any, Dict


@dataclass
class CaptionEntity:
    """
    Core business entity representing a generated caption.
    
    This is a pure domain entity with no dependencies on frameworks or external libraries.
    Contains business validation logic and entity behavior.
    """
    
    short_caption: str
    long_description: str
    hashtags: list[str]
    cta: str  # Call to action
    
    def __post_init__(self) -> None:
        """Validate entity invariants after initialization."""
        self.validate()
    
    def validate(self) -> None:
        """
        Validate business rules for the caption entity.
        
        Raises:
            ValueError: If any business rule is violated
        """
        if not self.short_caption or len(self.short_caption.strip()) == 0:
            raise ValueError("Short caption cannot be empty")
        
        if not self.long_description or len(self.long_description.strip()) == 0:
            raise ValueError("Long description cannot be empty")
        
        if not self.cta or len(self.cta.strip()) == 0:
            raise ValueError("CTA cannot be empty")
        
        if len(self.hashtags) == 0:
            raise ValueError("At least one hashtag is required")
        
        if len(self.hashtags) > 10:
            raise ValueError("Too many hashtags (maximum 10)")
        
        # Validate hashtags don't contain # symbol
        for tag in self.hashtags:
            if "#" in tag:
                raise ValueError(f"Hashtag '{tag}' should not contain # symbol")
            if not tag or len(tag.strip()) == 0:
                raise ValueError("Hashtags cannot be empty")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert entity to dictionary representation."""
        return {
            "short_caption": self.short_caption,
            "long_description": self.long_description,
            "hashtags": self.hashtags,
            "cta": self.cta,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CaptionEntity":
        """
        Create entity from dictionary representation.
        
        Args:
            data: Dictionary with caption data
            
        Returns:
            CaptionEntity instance
        """
        return cls(
            short_caption=data["short_caption"],
            long_description=data["long_description"],
            hashtags=data["hashtags"],
            cta=data["cta"],
        )
