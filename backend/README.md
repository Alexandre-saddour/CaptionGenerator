# 🌟 AI Caption Generator Backend

A production-ready FastAPI backend for generating social media captions using Google Gemini and OpenAI GPT-4 Vision. Built with **Clean Architecture** principles.

## 🏗️ Architecture

This project follows a pragmatic **Clean Architecture** with 4 distinct layers:

```
app/
├── domain/          # ⭐ Pure Business Logic
│   ├── entities.py  # Business objects (CaptionEntity)
│   └── ports.py     # Abstract interfaces (AIProviderPort)
│
├── application/     # ⭐ Use Cases
│   └── usecases/    # Orchestration logic (GenerateCaptionUseCase)
│
├── api/             # ⭐ Interface Adapters (HTTP)
│   ├── v1/          # API Version 1
│   └── schemas/     # Pydantic models for request/response
│
├── infrastructure/  # ⭐ External Implementations
│   └── providers/   # AI integrations (Gemini, OpenAI)
│
└── core/            # 🔧 Cross-cutting concerns
    ├── config.py    # Pydantic Settings
    ├── logging.py   # Structured logging
    └── security.py  # Rate limiting & validation
```

## ✨ Features

- **Multi-Provider Support**: Switch between Google Gemini and OpenAI GPT-4o.
- **Clean Architecture**: Decoupled, testable, and maintainable code.
- **Modern Python**: Uses Python 3.10+, Pydantic v2, and `uv` for packaging.
- **Production Ready**:
  - 🛡️ **Rate Limiting**: Per-IP limits using SlowAPI.
  - 🔒 **Security**: File size & MIME type validation.
  - 📝 **Structured Logging**: JSON logs for production.
  - 🔄 **Async/Await**: Fully asynchronous I/O.
  - 🌐 **CORS**: Configured for frontend integration.

## 🚀 Getting Started

### Prerequisites

- Python 3.10 or higher
- API Keys for Google Gemini and/or OpenAI

### Installation

1. **Clone the repository**
   ```bash
   git clone <repo-url>
   cd backend
   ```

2. **Create a virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -e .
   ```

4. **Configure Environment**
   Copy `.env.example` to `.env` and add your API keys:
   ```bash
   cp .env.example .env
   ```

### Running the Server

Start the development server:
```bash
uvicorn app.main:app --reload --port 8000
```

The API will be available at:
- **Docs**: http://localhost:8000/docs
- **API**: http://localhost:8000/api/v1/

## 🔌 API Endpoints

### `POST /api/v1/generate-caption`
Generate a caption from an uploaded image.

**Parameters:**
- `file`: Image file (JPEG, PNG, WebP, GIF)
- `context`: (Optional) Tone or context description
- `provider`: (Optional) `gemini` or `openai`

### `GET /api/v1/providers`
List available AI providers.

### `GET /api/v1/`
Health check and status.

## 🛠️ Development

### Project Structure
- **Domain**: Pure Python, no imports from other layers.
- **Application**: Depends only on Domain.
- **API/Infrastructure**: Depend on Application and Domain.

### Adding a New Provider
1. Create a new class in `app/infrastructure/providers/` implementing `AIProviderPort`.
2. Add it to `ProviderFactory`.
3. Update `Settings` to include its API key.
