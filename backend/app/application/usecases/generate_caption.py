from typing import Any, Dict, List, Optional
"""Generate caption use case - Application business logic orchestration."""

from app.domain.entities import CaptionEntity
from app.domain.errors import InvalidImageError, InvalidProviderError
from app.domain.ports import AIProviderPort, LoggerPort
from app.domain.value_objects import ImageContext, MimeType, ProviderName


class GenerateCaptionUseCase:
    """
    Use case for generating captions from images.
    
    This orchestrates the caption generation workflow:
    1. Validates inputs using domain value objects
    2. Delegates to AI provider through port
    3. Validates and returns domain entity
    
    Depends only on domain layer (entities, value objects, ports).
    """
    
    def __init__(self, provider: AIProviderPort, logger: LoggerPort):
        """
        Initialize use case with dependencies.
        
        Args:
            provider: AI provider implementation (injected)
            logger: Logger implementation (injected)
        """
        self._provider = provider
        self._logger = logger
    
    async def execute(
        self,
        image_data: bytes,
        mime_type_str: str,
        context_str: Optional[str],
        provider_name_str: str,
    ) -> CaptionEntity:
        """
        Execute the caption generation use case.
        
        Args:
            image_data: Raw image bytes
            mime_type_str: MIME type string
            context_str: Optional context/tone string
            provider_name_str: AI provider name string
            
        Returns:
            CaptionEntity with generated content
            
        Raises:
            InvalidImageError: If image data is invalid
            InvalidProviderError: If provider is invalid
            AIProviderUnavailableError: If provider service fails
            ValueError: If inputs violate domain rules
        """
        # Log start
        self._logger.info(
            "Starting caption generation",
            provider=provider_name_str,
            has_context=context_str is not None,
            image_size=len(image_data),
        )
        
        # Validate inputs using domain value objects
        try:
            mime_type = MimeType(mime_type_str)
            context = ImageContext(context_str)
            provider_name = ProviderName.from_string(provider_name_str)
        except ValueError as e:
            self._logger.warning(f"Input validation failed: {e}")
            raise
        
        # Validate image data
        if len(image_data) == 0:
            raise InvalidImageError("Image data is empty")
        
        # Log validated inputs
        self._logger.debug(
            "Inputs validated",
            mime_type=str(mime_type),
            has_context=context.has_context(),
            provider=provider_name.value,
        )
        
        # Generate caption through provider port
        try:
            entity = await self._provider.generate_caption(
                image_data=image_data,
                mime_type=mime_type.value,
                context=context.value,
            )
        except Exception as e:
            self._logger.error(
                f"Caption generation failed: {e}",
                provider=provider_name.value,
            )
            raise
        
        # Validate returned entity
        entity.validate()
        
        # Log success
        self._logger.info(
            "Caption generated successfully",
            provider=provider_name.value,
            hashtag_count=len(entity.hashtags),
        )
        
        return entity
