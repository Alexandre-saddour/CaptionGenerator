"""API v1 router - Aggregates all v1 endpoints."""

from fastapi import APIRouter

from .endpoints import captions, health

# Create v1 router
router = APIRouter()

# Include endpoint routers
router.include_router(health.router)
router.include_router(captions.router)
