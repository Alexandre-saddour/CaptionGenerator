from typing import Any, Dict, List, Optional
"""Ollama AI provider implementation."""

import base64
import json
import httpx

from app.domain.entities import CaptionEntity
from app.domain.errors import AIProviderUnavailableError, InvalidCaptionDataError
from app.domain.ports import AIProviderPort


class OllamaProvider(AIProviderPort):
    """Ollama AI provider implementing AIProviderPort."""
    
from app.domain.prompts import CAPTION_GENERATION_PROMPT

class OllamaProvider(AIProviderPort):
    """Ollama AI provider implementing AIProviderPort."""
    
    SYSTEM_PROMPT = CAPTION_GENERATION_PROMPT
    
    def __init__(self, base_url: str, model: str = "llava"):
        """
        Initialize Ollama provider.
        
        Args:
            base_url: Ollama API base URL
            model: Model name (default: llava)
        """
        self.base_url = base_url.rstrip('/')
        self.model = model
    
    async def generate_caption(
        self,
        image_data: bytes,
        mime_type: str,
        context: Optional[str] = None,
    ) -> CaptionEntity:
        """Generate caption using Ollama API."""
        # Prepare prompt
        prompt = self.SYSTEM_PROMPT
        if context:
            prompt += f"\n\nContext/Tone: {context}"
        
        # Encode image
        base64_image = base64.b64encode(image_data).decode('utf-8')
        
        # Prepare request payload
        payload = {
            "model": self.model,
            "prompt": prompt,
            "images": [base64_image],
            "stream": False,
            "format": "json"  # Enforce JSON mode if supported by model/version
        }
        
        # Call Ollama API
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/api/generate",
                    json=payload,
                    timeout=300.0  # Local inference can be slow
                )
                response.raise_for_status()
                result = response.json()
                response_text = result.get("response", "")
        except Exception as e:
            raise AIProviderUnavailableError("ollama", str(e))
        
        # Extract and parse JSON
        try:
            # Try parsing directly first
            json_data = json.loads(response_text)
        except json.JSONDecodeError:
            # Fallback: try to extract JSON from text if it contains extra text
            try:
                json_text = self._extract_json(response_text)
                json_data = json.loads(json_text)
            except Exception as e:
                raise InvalidCaptionDataError(
                    f"Failed to parse JSON from Ollama response: {e}",
                    raw_data=response_text
                )
        
        # Convert to entity
        try:
            entity = CaptionEntity.from_dict(json_data)
        except (KeyError, ValueError) as e:
            raise InvalidCaptionDataError(
                f"Invalid caption data format: {e}",
                raw_data=str(json_data)
            )
        
        return entity
    
    @staticmethod
    def _extract_json(text: str) -> str:
        """Extract JSON from response text."""
        text = text.strip()
        start = text.find('{')
        end = text.rfind('}')
        
        if start != -1 and end != -1:
            return text[start:end+1]
        return text
