"""
SAP TestOS - Core Configuration
Environment settings, database setup, and application constants
"""
import os
from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional


class Settings(BaseSettings):
    """Application settings with environment variable support"""
    
    # Application
    APP_NAME: str = "SAP TestOS"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    API_PREFIX: str = "/api/v1"
    
    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./testos.db"
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20
    DB_POOL_TIMEOUT: int = 30
    DB_POOL_RECYCLE: int = 1800
    
    # AI/LLM Configuration
    LLM_PROVIDER: str = "ollama"  # ollama, openai, anthropic
    LLM_MODEL: str = "llama3.2"  # Default free model
    LLM_BASE_URL: str = "http://localhost:11434"
    LLM_API_KEY: Optional[str] = None
    LLM_TIMEOUT: int = 60
    LLM_MAX_TOKENS: int = 4096
    LLM_TEMPERATURE: float = 0.3
    
    # Rate Limiting
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW: int = 60  # seconds
    
    # Concurrency
    MAX_CONCURRENT_REQUESTS: int = 50
    SEMAPHORE_LIMIT: int = 20
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # CORS
    CORS_ORIGINS: list = ["http://localhost:3000", "http://localhost:5173"]
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"  # Ignore extra fields from .env


@lru_cache()
def get_settings() -> Settings:
    """Cached settings instance"""
    return Settings()


settings = get_settings()
