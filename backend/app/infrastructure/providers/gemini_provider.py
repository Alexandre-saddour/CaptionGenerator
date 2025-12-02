from typing import Any, Dict, List, Optional
"""Gemini AI provider implementation."""

import base64
import json

import google.generativeai as genai

from app.domain.entities import CaptionEntity
from app.domain.errors import AIProviderUnavailableError, InvalidCaptionDataError
from app.domain.ports import AIProviderPort


class GeminiProvider(AIProviderPort):
    """Gemini AI provider implementing AIProviderPort."""
    
    SYSTEM_PROMPT = """You are an expert social media content creator and copywriter. 
Analyze the provided image and generate engaging, context-aware content.

You MUST respond with a valid JSON object in the following exact format:
{
    "short_caption": "A brief, engaging caption suitable for Instagram (1-2 sentences)",
    "long_description": "A detailed, professional description suitable for LinkedIn or blog posts (2-3 paragraphs)",
    "hashtags": ["hashtag1", "hashtag2", "hashtag3", "hashtag4", "hashtag5"],
    "cta": "A compelling call-to-action (1 sentence)"
}

Important:
- Adapt the tone and style based on the provided context/tone
- Make hashtags relevant and popular (without the # symbol)
- Ensure the CTA is actionable and engaging
- Return ONLY valid JSON, no additional text"""
    
    def __init__(self, api_key: str):
        """
        Initialize Gemini provider.
        
        Args:
            api_key: Gemini API key
        """
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash')
    
    async def generate_caption(
        self,
        image_data: bytes,
        mime_type: str,
        context: Optional[str] = None,
    ) -> CaptionEntity:
        """Generate caption using Gemini API."""
        # Prepare prompt
        user_prompt = self.SYSTEM_PROMPT
        if context:
            user_prompt += f"\n\nContext/Tone: {context}"
        
        # Encode image
        base64_image = base64.b64encode(image_data).decode('utf-8')
        image_part = {
            'mime_type': mime_type,
            'data': base64_image
        }
        
        # Generate content
        try:
            response = self.model.generate_content([user_prompt, image_part])
            response_text = response.text.strip()
        except Exception as e:
            raise AIProviderUnavailableError("gemini", str(e))
        
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
