"""FastAPI application factory - Main entry point."""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from app.api.v1 import router as v1_router
from app.core.config import get_settings
from app.core.logging import get_logger, setup_logging
from app.core.security import get_rate_limiter
from app.domain.errors import CaptionGenerationError


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Lifespan context manager for startup/shutdown events.
    
    Args:
        app: FastAPI application
        
    Yields:
        None
    """
    # Startup
    settings = get_settings()
    setup_logging(settings)
    logger = get_logger(__name__)
    
    logger.info(
        "🚀 Caption Generator API starting",
        environment=settings.environment,
        default_provider=settings.default_ai_provider,
        available_providers=settings.available_providers,
    )
    
    yield
    
    # Shutdown
    logger.info("👋 Caption Generator API shutting down")


def create_app() -> FastAPI:
    """
    Create and configure FastAPI application.
    
    Returns:
        Configured FastAPI app
    """
    settings = get_settings()
    
    # Create app
    app = FastAPI(
        title="Caption Generator API",
        version="1.0.0",
        description="AI-powered caption generation with Clean Architecture",
        lifespan=lifespan,
    )
    
    # CORS middleware (must be first)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Rate limiting middleware
    rate_limiter = get_rate_limiter()
    app.state.limiter = rate_limiter
    app.add_middleware(SlowAPIMiddleware)
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    
    # Error handlers for domain exceptions
    @app.exception_handler(CaptionGenerationError)
    async def caption_generation_error_handler(
        request: Request,
        exc: CaptionGenerationError
    ) -> JSONResponse:
        """Handle domain exceptions by converting to HTTP responses."""
        return JSONResponse(
            status_code=500,
            content={"detail": str(exc)}
        )
    
    # Mount API router with /api/v1 prefix
    app.include_router(v1_router.router, prefix="/api/v1")
    
    return app


# Create app instance
app = create_app()
