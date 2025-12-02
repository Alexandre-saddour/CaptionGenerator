from typing import Any, Dict, List, Optional
"""Application configuration using Pydantic Settings."""

from functools import lru_cache
from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    
    Uses Pydantic v2 for validation and type safety.
    """
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )
    
    # AI Provider Configuration
    gemini_api_key: Optional[str] = Field(default=None, description="Google Gemini API key")
    openai_api_key: Optional[str] = Field(default=None, description="OpenAI API key")
    ollama_base_url: str = Field(default="http://localhost:11434", description="Ollama Base URL")
    default_ai_provider: str = Field(default="gemini", description="Default AI provider")
    
    # Application Configuration
    environment: Literal["development", "production"] = Field(
        default="development",
        description="Application environment"
    )
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = Field(
        default="INFO",
        description="Logging level"
    )
    
    # Security Configuration
    rate_limit_per_minute: int = Field(default=60, description="API rate limit per minute per IP")
    max_file_size_mb: int = Field(default=10, description="Maximum upload file size in MB")
    enable_auth: bool = Field(default=False, description="Enable authentication")
    
    # CORS Configuration
    cors_origins: str = Field(
        default="http://localhost:5173",
        description="Allowed CORS origins (comma-separated)"
    )
    
    @field_validator("default_ai_provider")
    @classmethod
    def validate_provider(cls, v: str) -> str:
        """Validate provider name."""
        if v.lower() not in ["gemini", "openai", "ollama"]:
            raise ValueError("default_ai_provider must be 'gemini', 'openai' or 'ollama'")
        return v.lower()
    
    @property
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return self.environment == "production"
    
    @property
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.environment == "development"
    
    @property
    def cors_origins_list(self) -> list[str]:
        """Get CORS origins as a list."""
        return [origin.strip() for origin in self.cors_origins.split(",")]
    
    @property
    def available_providers(self) -> list[str]:
        """Get list of configured providers."""
        providers = []
        if self.gemini_api_key:
            providers.append("gemini")
        if self.openai_api_key:
            providers.append("openai")
        # Ollama is always available if configured (default URL exists)
        # In production, you might want to check if it's reachable, but for now we assume it is if the URL is set
        if self.ollama_base_url:
            providers.append("ollama")
        return providers
    
    def get_provider_key(self, provider: str) -> Optional[str]:
        """Get API key for specific provider."""
        provider_lower = provider.lower()
        if provider_lower == "gemini":
            return self.gemini_api_key
        elif provider_lower == "openai":
            return self.openai_api_key
        elif provider_lower == "ollama":
            return self.ollama_base_url # Return base URL as "key" for factory
        return None
    
    def validate_providers(self) -> None:
        """Validate that at least one provider is configured."""
        if not self.gemini_api_key and not self.openai_api_key and not self.ollama_base_url:
            raise ValueError(
                "At least one AI provider must be configured "
                "(GEMINI_API_KEY, OPENAI_API_KEY, or OLLAMA_BASE_URL)"
            )
    
    @property
    def max_file_size_bytes(self) -> int:
        """Get max file size in bytes."""
        return self.max_file_size_mb * 1024 * 1024


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance.
    
    Uses lru_cache to ensure singleton pattern.
    """
    settings = Settings()
    settings.validate_providers()
    return settings
