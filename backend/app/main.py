"""
SAP TestOS - Main Application Entry Point
FastAPI application with all routers and middleware configured
"""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import init_db, close_db
from app.core.logging_config import setup_logging
from app.middleware.rate_limiter import RateLimitMiddleware
from app.routers import matchmaker_router, vlm_agent_router, self_healing_router

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"Database: {settings.DATABASE_URL}")
    logger.info(f"LLM Provider: {settings.LLM_PROVIDER}")
    
    # Initialize database
    await init_db()
    logger.info("Database initialized")
    
    yield
    
    # Shutdown
    logger.info("Shutting down application")
    await close_db()


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    description="""
## SAP TestOS - Intelligent SAP Testing Platform

**Three integrated modules for the complete SAP consulting lifecycle:**

### 🎯 Matchmaker (Pre-Sales)
- Intelligent consultant matching with multi-factor scoring
- Auto-generate professional Statements of Work (SoW)
- Win SAP S/4HANA migration contracts faster

### 🤖 VLM Agent (Execution)
- Convert manual test cases to Playwright scripts
- Hybrid DOM + Vision approach for SAP Fiori
- Page Object Model pattern for maintainability

### 🔧 Self-Healing (Operations)
- AST-based surgical selector patching
- Automatically fix broken tests after SAP patches
- Reduce test maintenance costs by 70%

**Target Market:** Mid-to-Tier 1 SAP Consultancies
**Pricing:** $2,500/mo + Usage-based LLM billing
    """,
    version=settings.APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add rate limiting middleware
app.add_middleware(
    RateLimitMiddleware,
    requests_per_window=settings.RATE_LIMIT_REQUESTS,
    window_seconds=settings.RATE_LIMIT_WINDOW
)


# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """Application health check"""
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION
    }


# Include routers
app.include_router(matchmaker_router.router, prefix=settings.API_PREFIX)
app.include_router(vlm_agent_router.router, prefix=settings.API_PREFIX)
app.include_router(self_healing_router.router, prefix=settings.API_PREFIX)


# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with API information"""
    return {
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "documentation": "/docs",
        "modules": {
            "matchmaker": f"{settings.API_PREFIX}/matchmaker",
            "vlm_agent": f"{settings.API_PREFIX}/vlm-agent",
            "self_healing": f"{settings.API_PREFIX}/self-healing"
        }
    }


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle uncaught exceptions"""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return {
        "error": "internal_server_error",
        "message": "An unexpected error occurred",
        "path": str(request.url.path)
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )
