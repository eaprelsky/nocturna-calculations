"""
API configuration module
"""
from pydantic_settings import BaseSettings
from pydantic import ConfigDict
from typing import List, Optional
import os
from functools import lru_cache

class Settings(BaseSettings):
    """API settings"""
    
    # API settings
    API_V1_PREFIX: str = "/v1"
    PROJECT_NAME: str = "Nocturna Calculations API"
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",  # Frontend development
        "http://localhost:8000",  # API development
        "https://calculations.nocturna.ru",  # Production
    ]
    
    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:postgres@localhost:5432/nocturna"
    )
    
    # Redis
    REDIS_URL: str = os.getenv(
        "REDIS_URL",
        "redis://localhost:6379/0"
    )
    
    # Rate limiting
    RATE_LIMIT_FREE: int = 100  # requests per hour
    RATE_LIMIT_BASIC: int = 1000
    RATE_LIMIT_PRO: int = 10000
    RATE_LIMIT_DEFAULT: int = 100
    RATE_LIMIT_PREMIUM: int = 1000
    RATE_LIMIT_WINDOW: int = 3600
    
    # Cache
    CACHE_TTL: int = 3600  # 1 hour in seconds
    
    # Cache key prefix (optional)
    CACHE_PREFIX: str = "calc:"
    
    # Redis configuration
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_MAX_CONNECTIONS: int = 10
    REDIS_SOCKET_TIMEOUT: int = 5
    REDIS_SOCKET_CONNECT_TIMEOUT: int = 5
    
    # Additional API settings that might come from env
    API_VERSION_PREFIX: str = "/v1"
    
    # User Management Settings
    ALLOW_USER_REGISTRATION: bool = True
    REGISTRATION_REQUIRES_APPROVAL: bool = False  # Future enhancement
    MAX_USERS_LIMIT: Optional[int] = None  # Future enhancement
    
    model_config = ConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="allow",  # Allow extra fields from .env
        frozen=True,  # Make the model immutable
    )

@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()

# Create settings instance
settings = get_settings() 