from typing import Any, Dict, List, Optional
"""Provider factory for creating AI provider instances."""

from app.domain.errors import InvalidProviderError
from app.domain.ports import AIProviderPort
from app.domain.value_objects import ProviderName

from .gemini_provider import GeminiProvider
from .openai_provider import OpenAIProvider
from .ollama_provider import OllamaProvider


class ProviderFactory:
    """Factory for creating AI provider instances."""
    
    @staticmethod
    def create(provider_name: ProviderName | str, api_key: str) -> AIProviderPort:
        """
        Create AI provider instance.
        
        Args:
            provider_name: Provider name (ProviderName enum or string)
            api_key: API key for the provider (or base URL for Ollama)
            
        Returns:
            AIProviderPort implementation
            
        Raises:
            InvalidProviderError: If provider is not supported
        """
        # Convert string to ProviderName if needed
        if isinstance(provider_name, str):
            try:
                provider_name = ProviderName.from_string(provider_name)
            except ValueError as e:
                raise InvalidProviderError(provider_name) from e
        
        # Create provider instance
        if provider_name == ProviderName.GEMINI:
            return GeminiProvider(api_key)
        elif provider_name == ProviderName.OPENAI:
            return OpenAIProvider(api_key)
        elif provider_name == ProviderName.OLLAMA:
            return OllamaProvider(base_url=api_key) # api_key is base_url for Ollama
        else:
            # Should never reach here due to enum validation
            available = [p.value for p in ProviderName]
            raise InvalidProviderError(str(provider_name), available)
