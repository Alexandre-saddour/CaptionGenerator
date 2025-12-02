"""Caption generation endpoints."""

from typing import Annotated, Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from pydantic import ValidationError

from app.api.deps import (
    get_ai_provider, 
    get_logger_dep, 
    get_provider_factory, 
    get_settings, 
    get_use_case, 
    validate_file_upload
)
from app.api.schemas.caption_response import CaptionResponseSchema
from app.application.usecases.generate_caption import GenerateCaptionUseCase
from app.core.config import Settings
from app.domain.errors import CaptionGenerationError
from app.domain.ports import LoggerPort
from app.infrastructure.providers.factory import ProviderFactory

router = APIRouter(tags=["captions"])


@router.post("/generate-caption", response_model=CaptionResponseSchema)
async def generate_caption(
    file: Annotated[UploadFile, Depends(validate_file_upload)],
    settings: Annotated[Settings, Depends(get_settings)],
    factory: Annotated[ProviderFactory, Depends(get_provider_factory)],
    logger: Annotated[LoggerPort, Depends(get_logger_dep)],
    context: Optional[str] = Form(None, description="Context or tone for the caption"),
    provider: Optional[str] = Form(None, description="AI provider to use (gemini or openai)"),
) -> CaptionResponseSchema:
    """
    Generate caption from uploaded image.
    
    Thin controller that:
    1. Extracts HTTP parameters
    2. Calls use case via dependency injection
    3. Converts entity to HTTP response
    4. Returns response
    
    Args:
        file: Uploaded image file (validated)
        settings: Application settings
        factory: Provider factory
        logger: Logger instance
        context: Optional context/tone
        provider: Optional provider choice
        
    Returns:
        CaptionResponseSchema with generated content
        
    Raises:
        HTTPException: On validation or generation errors
    """
    # Determine provider (use default if not specified)
    provider_name = provider if provider else settings.default_ai_provider
    
    # Validate provider choice
    if provider_name not in settings.available_providers:
        raise HTTPException(
            status_code=400,
            detail=f"Provider '{provider_name}' not available. "
                   f"Available: {', '.join(settings.available_providers)}"
        )
    
    # Get use case with correct provider
    try:
        ai_provider = get_ai_provider(provider_name, settings, factory)
        use_case = get_use_case(ai_provider, logger)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    # Read image data
    image_data = await file.read()
    
    # Execute use case
    try:
        entity = await use_case.execute(
            image_data=image_data,
            mime_type_str=file.content_type or "image/jpeg",
            context_str=context,
            provider_name_str=provider_name,
        )
    except CaptionGenerationError as e:
        # Domain errors -> HTTP errors
        raise HTTPException(status_code=500, detail=str(e))
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=f"Validation error: {e}")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {e}")
    
    # Convert entity to HTTP response
    return CaptionResponseSchema(
        short_caption=entity.short_caption,
        long_description=entity.long_description,
        hashtags=entity.hashtags,
        cta=entity.cta,
        provider=provider_name,
    )
