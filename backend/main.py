# main.py

import os
from typing import Optional
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, ValidationError
from dotenv import load_dotenv
import json

from ai_providers import AIProviderFactory

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Caption Generator API", 
    version="1.0.0",
    description="AI-powered caption generation with support for multiple AI providers"
)

# Configure CORS to allow React frontend (port 5173) to communicate
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for response validation
class CaptionResponse(BaseModel):
    short_caption: str
    long_description: str
    hashtags: list[str]
    cta: str
    provider: str  # Which AI provider was used

# Get API keys from environment
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Default provider (can be changed via environment variable)
DEFAULT_PROVIDER = os.getenv("DEFAULT_AI_PROVIDER", "gemini").lower()

# Validate that at least one provider is configured
if not GEMINI_API_KEY and not OPENAI_API_KEY:
    raise ValueError("At least one AI provider API key must be configured (GEMINI_API_KEY or OPENAI_API_KEY)")

# Determine which provider to use
if DEFAULT_PROVIDER == "gemini" and GEMINI_API_KEY:
    print(f"✓ Using Gemini AI as default provider")
elif DEFAULT_PROVIDER == "openai" and OPENAI_API_KEY:
    print(f"✓ Using OpenAI as default provider")
elif GEMINI_API_KEY:
    DEFAULT_PROVIDER = "gemini"
    print(f"⚠ Falling back to Gemini AI (default provider not available)")
elif OPENAI_API_KEY:
    DEFAULT_PROVIDER = "openai"
    print(f"⚠ Falling back to OpenAI (default provider not available)")


@app.get("/")
def read_root():
    """Health check endpoint"""
    available_providers = []
    if GEMINI_API_KEY:
        available_providers.append("gemini")
    if OPENAI_API_KEY:
        available_providers.append("openai")
    
    return {
        "status": "online",
        "message": "Caption Generator API is running",
        "version": "1.0.0",
        "default_provider": DEFAULT_PROVIDER,
        "available_providers": available_providers
    }


@app.get("/providers")
def list_providers():
    """List available AI providers"""
    providers = []
    
    if GEMINI_API_KEY:
        providers.append({
            "name": "gemini",
            "display_name": "Google Gemini",
            "is_default": DEFAULT_PROVIDER == "gemini"
        })
    
    if OPENAI_API_KEY:
        providers.append({
            "name": "openai",
            "display_name": "OpenAI GPT-4",
            "is_default": DEFAULT_PROVIDER == "openai"
        })
    
    return {
        "providers": providers,
        "default": DEFAULT_PROVIDER
    }


@app.post("/generate-caption", response_model=CaptionResponse)
async def generate_caption(
    file: UploadFile = File(..., description="Image file to analyze"),
    context: Optional[str] = Form(None, description="Context or tone for the caption"),
    provider: Optional[str] = Form(None, description="AI provider to use (gemini or openai)")
):
    """
    Generate captions, descriptions, hashtags, and CTA for an uploaded image.
    
    Args:
        file: Image file (JPEG, PNG, WebP, etc.)
        context: Optional context/tone for the generated content
        provider: Optional provider choice (defaults to DEFAULT_PROVIDER)
    
    Returns:
        CaptionResponse with generated content
    """
    try:
        # Validate file type
        allowed_types = ["image/jpeg", "image/jpg", "image/png", "image/webp", "image/gif"]
        if file.content_type not in allowed_types:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file type. Allowed types: {', '.join(allowed_types)}"
            )
        
        # Determine which provider to use
        selected_provider = provider.lower() if provider else DEFAULT_PROVIDER
        
        # Validate provider choice and API key availability
        if selected_provider == "gemini" and not GEMINI_API_KEY:
            raise HTTPException(
                status_code=400,
                detail="Gemini API key not configured"
            )
        elif selected_provider == "openai" and not OPENAI_API_KEY:
            raise HTTPException(
                status_code=400,
                detail="OpenAI API key not configured"
            )
        elif selected_provider not in ["gemini", "openai"]:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid provider: {selected_provider}. Must be 'gemini' or 'openai'"
            )
        
        # Get the appropriate API key
        api_key = GEMINI_API_KEY if selected_provider == "gemini" else OPENAI_API_KEY
        
        # Create the AI provider
        ai_provider = AIProviderFactory.create_provider(selected_provider, api_key)
        
        # Read image data
        image_data = await file.read()
        
        # Generate caption using the selected provider
        result = await ai_provider.generate_caption(
            image_data=image_data,
            mime_type=file.content_type,
            context=context
        )
        
        # Add provider info to response
        result["provider"] = selected_provider
        
        # Validate and return response
        validated_response = CaptionResponse(**result)
        return validated_response
        
    except HTTPException:
        raise
    except json.JSONDecodeError as e:
        print(f"JSON parsing error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to parse AI response. The {selected_provider} model did not return valid JSON."
        )
    except ValidationError as e:
        print(f"Validation error: {e}")
        raise HTTPException(
            status_code=500,
            detail="AI response did not match expected format"
        )
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while generating captions: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)