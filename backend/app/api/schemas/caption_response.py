"""HTTP response schemas - DTOs for API responses."""

from datetime import datetime

from pydantic import BaseModel, Field


class CaptionResponseSchema(BaseModel):
    """HTTP response schema for caption generation."""
    
    short_caption: str = Field(..., description="Brief caption for social media")
    long_description: str = Field(..., description="Detailed description for blogs/LinkedIn")
    hashtags: list[str] = Field(..., description="Relevant hashtags without # symbol")
    cta: str = Field(..., description="Call-to-action")
    provider: str = Field(..., description="AI provider used for generation")
    
    class Config:
        json_schema_extra = {
            "example": {
                "short_caption": "Amazing sunset over the mountains! 🌄",
                "long_description": "This breathtaking view captures...",
                "hashtags": ["sunset", "mountains", "nature", "photography", "beautiful"],
                "cta": "Double tap if you love sunsets!",
                "provider": "gemini"
            }
        }


class HealthResponseSchema(BaseModel):
    """Health check response schema."""
    
    status: str = Field(..., description="Service status")
    message: str = Field(..., description="Status message")
    version: str = Field(..., description="API version")
    default_provider: str = Field(..., description="Default AI provider")
    available_providers: list[str] = Field(..., description="Available AI providers")


class ProviderInfoSchema(BaseModel):
    """Provider information schema."""
    
    name: str = Field(..., description="Provider identifier")
    display_name: str = Field(..., description="Human-readable provider name")
    is_default: bool = Field(..., description="Whether this is the default provider")


class ProviderListResponseSchema(BaseModel):
    """Provider list response schema."""
    
    providers: list[ProviderInfoSchema] = Field(..., description="Available providers")
    default: str = Field(..., description="Default provider name")
