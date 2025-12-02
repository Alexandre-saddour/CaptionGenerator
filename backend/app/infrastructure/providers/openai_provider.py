from typing import Any, Dict, List, Optional
"""OpenAI provider implementation - Uses AsyncOpenAI for proper async/await."""

import base64
import json

from openai import AsyncOpenAI

from app.domain.entities import CaptionEntity
from app.domain.errors import AIProviderUnavailableError, InvalidCaptionDataError
from app.domain.ports import AIProviderPort


class OpenAIProvider(AIProviderPort):
    """OpenAI provider implementing AIProviderPort with async support."""
    
from app.domain.prompts import CAPTION_GENERATION_PROMPT

class OpenAIProvider(AIProviderPort):
    """OpenAI provider implementing AIProviderPort with async support."""
    
    SYSTEM_PROMPT = CAPTION_GENERATION_PROMPT
    
    def __init__(self, api_key: str):
        """
        Initialize OpenAI provider with async client.
        
        Args:
            api_key: OpenAI API key
        """
        self.client = AsyncOpenAI(api_key=api_key)
    
    async def generate_caption(
        self,
        image_data: bytes,
        mime_type: str,
        context: Optional[str] = None,
    ) -> CaptionEntity:
        """Generate caption using OpenAI Vision API with async/await."""
        # Prepare prompt
        user_prompt = self.SYSTEM_PROMPT
        if context:
            user_prompt += f"\n\nContext/Tone: {context}"
        
        # Encode image as data URL
        base64_image = base64.b64encode(image_data).decode('utf-8')
        data_url = f"data:{mime_type};base64,{base64_image}"
        
        # Generate content using async API
        try:
            response = await self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": user_prompt},
                            {
                                "type": "image_url",
                                "image_url": {"url": data_url}
                            }
                        ]
                    }
                ],
                max_tokens=1000
            )
            
            response_text = response.choices[0].message.content.strip()
        except Exception as e:
            raise AIProviderUnavailableError("openai", str(e))
        
        # Extract and parse JSON
        try:
            json_text = self._extract_json(response_text)
            result = json.loads(json_text)
        except json.JSONDecodeError as e:
            raise InvalidCaptionDataError(
                f"Failed to parse JSON: {e}",
                raw_data=response_text
            )
        
        # Convert to entity
        try:
            entity = CaptionEntity.from_dict(result)
        except (KeyError, ValueError) as e:
            raise InvalidCaptionDataError(
                f"Invalid caption data format: {e}",
                raw_data=json_text
            )
        
        return entity
    
    @staticmethod
    def _extract_json(text: str) -> str:
        """Extract JSON from response text that might be wrapped in markdown."""
        text = text.strip()
        
        # Remove markdown code blocks if present
        if text.startswith("```json"):
            text = text.split("```json")[1].split("```")[0].strip()
        elif text.startswith("```"):
            text = text.split("```")[1].split("```")[0].strip()
        
        return text
