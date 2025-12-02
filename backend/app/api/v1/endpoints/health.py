"""Health check endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.schemas.caption_response import (
    HealthResponseSchema,
    ProviderInfoSchema,
    ProviderListResponseSchema,
)
from app.core.config import Settings, get_settings

router = APIRouter(tags=["health"])


@router.get("/", response_model=HealthResponseSchema)
async def root_health_check(
    settings: Annotated[Settings, Depends(get_settings)]
) -> HealthResponseSchema:
    """
    Root health check endpoint.
    
    Returns basic service information and available providers.
    """
    return HealthResponseSchema(
        status="online",
        message="Caption Generator API is running",
        version="1.0.0",
        default_provider=settings.default_ai_provider,
        available_providers=settings.available_providers,
    )


@router.get("/health", response_model=HealthResponseSchema)
async def detailed_health_check(
    settings: Annotated[Settings, Depends(get_settings)]
) -> HealthResponseSchema:
    """
    Detailed health check endpoint.
    
    Can be extended with database connectivity checks, etc.
    """
    return HealthResponseSchema(
        status="online",
        message="All systems operational",
        version="1.0.0",
        default_provider=settings.default_ai_provider,
        available_providers=settings.available_providers,
    )


@router.get("/providers", response_model=ProviderListResponseSchema)
async def list_providers(
    settings: Annotated[Settings, Depends(get_settings)]
) -> ProviderListResponseSchema:
    """
    List available AI providers.
    
    Returns configured providers with metadata.
    """
    providers = []
    
    if "gemini" in settings.available_providers:
        providers.append(
            ProviderInfoSchema(
                name="gemini",
                display_name="Google Gemini",
                is_default=settings.default_ai_provider == "gemini"
            )
        )
    
    if "openai" in settings.available_providers:
        providers.append(
            ProviderInfoSchema(
                name="openai",
                display_name="OpenAI GPT-4",
                is_default=settings.default_ai_provider == "openai"
            )
        )
    
    return ProviderListResponseSchema(
        providers=providers,
        default=settings.default_ai_provider
    )
