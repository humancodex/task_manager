from typing import Optional, List
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
import os


class Settings(BaseSettings):
    app_name: str = "Task Management API"
    app_version: str = "1.0.0"
    debug: bool = False
    environment: str = Field(default="development", description="Environment: development, staging, production")
    
    # Security configuration
    secret_key: str = Field(default="", description="Secret key for cryptographic operations")
    cors_origins: str = Field(
        default="http://localhost:3000,http://localhost:8080",
        description="Allowed CORS origins (comma-separated)"
    )
    cors_allow_credentials: bool = True
    
    # Rate limiting configuration
    rate_limit_enabled: bool = True
    rate_limit_requests: int = Field(default=100, description="Requests per minute per IP")
    rate_limit_window: int = Field(default=60, description="Rate limit window in seconds")
    
    # Database configuration - async PostgreSQL
    database_url: str = "postgresql+asyncpg://taskuser:taskpass@localhost:5432/taskdb"
    
    # Synchronous database URL for alembic migrations
    database_url_sync: str = "postgresql+psycopg2://taskuser:taskpass@localhost:5432/taskdb"
    
    # Server configuration
    host: str = "0.0.0.0"
    port: int = 8000
    
    # Logging configuration
    log_level: str = "INFO"
    log_format: str = "json"
    
    # Security headers configuration
    security_headers_enabled: bool = True
    
    @property
    def is_production(self) -> bool:
        """Check if running in production environment"""
        return self.environment.lower() == "production"
    
    @property
    def is_development(self) -> bool:
        """Check if running in development environment"""
        return self.environment.lower() == "development"
    
    def get_cors_origins(self) -> List[str]:
        """Get CORS origins based on environment"""
        # Parse comma-separated string into list
        origins = [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]
        
        if self.environment == "production":
            # In production, only allow specific domains
            return [origin for origin in origins if not origin.startswith("http://localhost")]
        return origins
    
    # Pydantic Settings (v2): read from .env and ignore unknown variables
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()