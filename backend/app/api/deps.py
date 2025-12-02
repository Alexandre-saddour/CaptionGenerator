"""FastAPI dependency injection - Wires together use cases and implementations."""

from typing import Annotated

from fastapi import Depends, Request, UploadFile

from app.application.usecases.generate_caption import GenerateCaptionUseCase
from app.core.config import Settings, get_settings
from app.core.logging import get_logger
from app.core.security import FileValidator
from app.domain.ports import AIProviderPort, LoggerPort
from app.infrastructure.providers.factory import ProviderFactory


def get_logger_dep(request: Request) -> LoggerPort:
    """
    Get logger with request context.
    
    Args:
        request: FastAPI request
        
    Returns:
        LoggerPort implementation
    """
    request_id = request.headers.get("X-Request-ID", None)
    return get_logger(__name__, request_id)


def get_provider_factory() -> ProviderFactory:
    """
    Get provider factory instance.
    
    Returns:
        ProviderFactory
    """
    return ProviderFactory()


def get_file_validator(
    settings: Annotated[Settings, Depends(get_settings)]
) -> FileValidator:
    """
    Get file validator instance.
    
    Args:
        settings: Application settings
        
    Returns:
        FileValidator
    """
    return FileValidator(settings)


async def validate_file_upload(
    file: UploadFile,
    validator: Annotated[FileValidator, Depends(get_file_validator)]
) -> UploadFile:
    """
    Validate uploaded file.
    
    Args:
        file: Uploaded file
        validator: File validator
        
    Returns:
        Validated file
        
    Raises:
        HTTPException: If validation fails
    """
    await validator.validate(file)
    return file


def get_ai_provider(
    provider_name: str,
    settings: Annotated[Settings, Depends(get_settings)],
    factory: Annotated[ProviderFactory, Depends(get_provider_factory)]
) -> AIProviderPort:
    """
    Get AI provider instance.
    
    Args:
        provider_name: Provider name
        settings: Application settings
        factory: Provider factory
        
    Returns:
        AIProviderPort implementation
        
    Raises:
        HTTPException: If provider is invalid or API key not configured
    """
    api_key = settings.get_provider_key(provider_name)
    if not api_key:
        from fastapi import HTTPException
        raise HTTPException(
            status_code=400,
            detail=f"Provider '{provider_name}' API key not configured"
        )
    
    return factory.create(provider_name, api_key)


def get_use_case(
    provider: AIProviderPort,
    logger: Annotated[LoggerPort, Depends(get_logger_dep)]
) -> GenerateCaptionUseCase:
    """
    Get caption generation use case with dependencies.
    
    Args:
        provider: AI provider
        logger: Logger
        
    Returns:
        GenerateCaptionUseCase
    """
    return GenerateCaptionUseCase(provider=provider, logger=logger)
