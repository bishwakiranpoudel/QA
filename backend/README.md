# SAP TestOS Backend

Production-ready FastAPI backend for SAP TestOS platform.

## Architecture

```
app/
├── main.py              # Application entry point
├── core/                # Core configuration
│   ├── config.py        # Settings & environment variables
│   ├── database.py      # Async DB session management
│   └── logging_config.py
├── middleware/          # Custom middleware
│   └── rate_limiter.py  # Rate limiting middleware
├── models/              # SQLAlchemy models
│   └── entities.py      # Database entities
├── schemas/             # Pydantic schemas
│   └── responses.py     # Request/Response models
├── repositories/        # Data access layer
│   ├── base.py          # Generic repository
│   └── consultant_repository.py
├── services/            # Business logic
│   ├── llm_service.py   # Unified LLM interface
│   ├── matchmaker_service.py
│   ├── vlm_agent_service.py
│   └── self_healing_service.py
├── routers/             # API endpoints
│   ├── matchmaker_router.py
│   ├── vlm_agent_router.py
│   └── self_healing_router.py
└── seed.py              # Database seeder
```

## Features

### Enterprise-Grade Patterns
- **Repository Pattern**: Clean separation of data access logic
- **Service Layer**: Business logic isolated from API routes
- **Async/Await**: Full async support for high concurrency
- **Connection Pooling**: Efficient database connection management
- **Rate Limiting**: Protects against abuse

### AI/LLM Integration
- **Multi-Provider Support**: Ollama (free), OpenAI, Anthropic
- **Automatic Fallback**: Cascades through providers on failure
- **Rule-Based Fallback**: Intelligent templates when no LLM available

### SAP-Specific Optimizations
- Module synonym matching (14 SAP modules)
- Auto-generated ID detection for selectors
- SAP BusyIndicator handling
- Fiori-specific selector strategies

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Seed database
python -m app.seed

# Run server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## API Documentation

Once running, access:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- Health Check: http://localhost:8000/health

## Environment Variables

Create `.env` file:

```env
# Application
DEBUG=false
API_PREFIX=/api/v1

# Database
DATABASE_URL=sqlite+aiosqlite:///./testos.db

# LLM (Optional - works without)
LLM_PROVIDER=ollama
LLM_MODEL=llama3.2
LLM_BASE_URL=http://localhost:11434
LLM_API_KEY=  # For OpenAI/Anthropic

# Rate Limiting
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=60
```

## Testing

```bash
# Test health endpoint
curl http://localhost:8000/health

# Get consultants
curl http://localhost:8000/api/v1/matchmaker/consultants

# Match consultants
curl -X POST http://localhost:8000/api/v1/matchmaker/match \
  -H "Content-Type: application/json" \
  -d '{"project_description": "S/4HANA migration for FICO module", "min_experience": 5}'
```
