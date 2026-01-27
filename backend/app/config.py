"""
Configuration module for ATS Analyzer
"""

from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    """Application settings."""
    
    # API Configuration
    environment: str = os.getenv("ENVIRONMENT", "development")
    debug: bool = os.getenv("DEBUG", "true").lower() == "true"
    api_host: str = os.getenv("API_HOST", "0.0.0.0")
    api_port: int = int(os.getenv("API_PORT", "8000"))
    api_workers: int = int(os.getenv("API_WORKERS", "4"))
    
    # Database
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./ats_analyzer.db")
    enable_database: bool = os.getenv("ENABLE_DATABASE", "false").lower() == "true"
    
    # Scoring
    default_strict_mode: bool = False
    enable_rewrite_suggestions: bool = False
    
    # CORS
    cors_origins: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173"
    ]
    
    # Logging
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
