"""
AI Provider Base Class and Implementations

This module defines an abstract base class for AI providers and concrete implementations
for Gemini and OpenAI Vision APIs. This architecture allows easy addition of new providers.
"""

import base64
import json
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
import google.generativeai as genai
from openai import OpenAI


class AIProvider(ABC):
    """Abstract base class for AI caption generation providers"""
    
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

    @abstractmethod
    async def generate_caption(
        self, 
        image_data: bytes, 
        mime_type: str, 
        context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate caption content from an image.
        
        Args:
            image_data: Raw image bytes
            mime_type: MIME type of the image
            context: Optional context/tone for the generation
            
        Returns:
            Dictionary with short_caption, long_description, hashtags, and cta
        """
        pass

    @staticmethod
    def _extract_json(text: str) -> str:
        """Extract JSON from response text that might be wrapped in markdown code blocks"""
        text = text.strip()
        
        # Remove markdown code blocks if present
        if text.startswith("```json"):
            text = text.split("```json")[1].split("```")[0].strip()
        elif text.startswith("```"):
            text = text.split("```")[1].split("```")[0].strip()
        
        return text


class GeminiProvider(AIProvider):
    """Gemini AI provider implementation"""
    
    def __init__(self, api_key: str):
        """
        Initialize Gemini provider.
        
        Args:
            api_key: Gemini API key
        """
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
    
    async def generate_caption(
        self, 
        image_data: bytes, 
        mime_type: str, 
        context: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate caption using Gemini API"""
        
        # Prepare the prompt with context
        user_prompt = self.SYSTEM_PROMPT
        if context and context.strip():
            user_prompt += f"\n\nContext/Tone: {context.strip()}"
        
        # Encode image to base64
        base64_image = base64.b64encode(image_data).decode('utf-8')
        
        # Prepare the image part
        image_part = {
            'mime_type': mime_type,
            'data': base64_image
        }
        
        # Generate content
        response = self.model.generate_content([user_prompt, image_part])
        response_text = response.text.strip()
        
        # Extract and parse JSON
        json_text = self._extract_json(response_text)
        result = json.loads(json_text)
        
        return result


class OpenAIProvider(AIProvider):
    """OpenAI Vision API provider implementation"""
    
    def __init__(self, api_key: str):
        """
        Initialize OpenAI provider.
        
        Args:
            api_key: OpenAI API key
        """
        self.client = OpenAI(api_key=api_key)
    
    async def generate_caption(
        self, 
        image_data: bytes, 
        mime_type: str, 
        context: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate caption using OpenAI Vision API"""
        
        # Prepare the prompt with context
        user_prompt = self.SYSTEM_PROMPT
        if context and context.strip():
            user_prompt += f"\n\nContext/Tone: {context.strip()}"
        
        # Encode image to base64
        base64_image = base64.b64encode(image_data).decode('utf-8')
        data_url = f"data:{mime_type};base64,{base64_image}"
        
        # Generate content using GPT-4 Vision
        response = self.client.chat.completions.create(
            model="gpt-4o-mini",  # Using gpt-4o-mini for vision capabilities
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
        
        # Extract and parse JSON
        json_text = self._extract_json(response_text)
        result = json.loads(json_text)
        
        return result


class AIProviderFactory:
    """Factory class to create AI providers"""
    
    @staticmethod
    def create_provider(provider_name: str, api_key: str) -> AIProvider:
        """
        Create an AI provider instance.
        
        Args:
            provider_name: Name of the provider ('gemini' or 'openai')
            api_key: API key for the provider
            
        Returns:
            AIProvider instance
            
        Raises:
            ValueError: If provider name is not supported
        """
        providers = {
            'gemini': GeminiProvider,
            'openai': OpenAIProvider,
        }
        
        provider_class = providers.get(provider_name.lower())
        if not provider_class:
            raise ValueError(
                f"Unsupported provider: {provider_name}. "
                f"Supported providers: {', '.join(providers.keys())}"
            )
        
        return provider_class(api_key)
