import os
from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        case_sensitive=True,
        env_file=".env",
        extra="allow"
    )

    PROJECT_NAME: str = "FestiveAI"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    # Security
    SECRET_KEY: str = "festiveai_super_secret_jwt_signing_key_change_in_production_2026"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    
    # Sensitive Data Encryption (Fernet 32-byte urlsafe base64 key)
    # Default provided for out-of-the-box local development
    ENCRYPTION_KEY: str = "gAAAAABmFz-mockEncryptionKeyFestiveAI32BytesNeededForFernet="
    
    # Database (Defaults to SQLite for instant local run, supports PostgreSQL)
    DATABASE_URL: str = "sqlite:///./festiveai.db"
    
    # Storage & Media Assets
    MEDIA_ROOT: str = "./media"
    STATIC_UPLOADS: str = "./media/uploads"
    GENERATED_ASSETS: str = "./media/generated"
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
        "*"
    ]
    
    # AI Providers (Pluggable)
    DEFAULT_AI_PROVIDER: str = "mock"  # "gemini", "openai", "mock"
    GEMINI_API_KEY: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None
    
    # Social Platforms (OAuth & APIs)
    # Meta / Instagram
    INSTAGRAM_APP_ID: Optional[str] = None
    INSTAGRAM_APP_SECRET: Optional[str] = None
    INSTAGRAM_REDIRECT_URI: str = "http://localhost:8000/api/v1/accounts/oauth/callback/instagram"
    
    # LinkedIn
    LINKEDIN_CLIENT_ID: Optional[str] = None
    LINKEDIN_CLIENT_SECRET: Optional[str] = None
    LINKEDIN_REDIRECT_URI: str = "http://localhost:8000/api/v1/accounts/oauth/callback/linkedin"
    
    # Automation Worker
    AUTONOMOUS_WORKER_INTERVAL_SECONDS: int = 60
    DEFAULT_LEAD_TIME_DAYS: int = 7
    DEFAULT_PUBLISH_TIME: str = "09:00:00"
    DEFAULT_TIMEZONE: str = "Asia/Kolkata"

settings = Settings()

# Ensure media directories exist
os.makedirs(settings.MEDIA_ROOT, exist_ok=True)
os.makedirs(settings.STATIC_UPLOADS, exist_ok=True)
os.makedirs(settings.GENERATED_ASSETS, exist_ok=True)
