"""
Configuration Management System
Centralized settings with environment variable validation
"""

from typing import List, Optional
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables
    Multi-tenant aware configuration
    """
    
    # ============================================
    # Application Settings
    # ============================================
    APP_NAME: str = "AI Portfolio Platform"
    APP_VERSION: str = "0.1.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    # Server Configuration
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    
    # ============================================
    # Security Configuration
    # ============================================
    SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION: int = 86400  # 24 hours
    
    # Admin Credentials
    ADMIN_USERNAME: str = "admin"
    ADMIN_PASSWORD: str  # Will be hashed on first run
    
    # ============================================
    # OpenAI Configuration
    # ============================================
    OPENAI_API_KEY: str
    OPENAI_MODEL: str = "gpt-4-turbo-preview"
    OPENAI_EMBEDDING_MODEL: str = "text-embedding-ada-002"
    OPENAI_MAX_TOKENS: int = 1000
    OPENAI_TEMPERATURE: float = 0.7
    
    @field_validator("OPENAI_API_KEY")
    @classmethod
    def validate_openai_key(cls, v: str) -> str:
        if not v.startswith("sk-"):
            raise ValueError("OpenAI API key must start with 'sk-'")
        return v
    
    # ============================================
    # MongoDB Configuration
    # ============================================
    MONGODB_URL: str
    MONGODB_DB_NAME: str = "ai_portfolio"
    MONGODB_MAX_CONNECTIONS: int = 10
    MONGODB_MIN_CONNECTIONS: int = 2
    
    @field_validator("MONGODB_URL")
    @classmethod
    def validate_mongodb_url(cls, v: str) -> str:
        if not v.startswith("mongodb"):
            raise ValueError("MongoDB URL must start with 'mongodb://' or 'mongodb+srv://'")
        return v
    
    # ============================================
    # Qdrant Configuration
    # ============================================
    QDRANT_URL: str = Field(default="http://localhost:6333", env="QDRANT_URL")
    QDRANT_API_KEY: Optional[str] = Field(default=None, env="QDRANT_API_KEY")
    QDRANT_COLLECTION_PREFIX: str = Field(default="portfolio", env="QDRANT_COLLECTION_PREFIX")
    VECTOR_DIMENSION: int = Field(default=1536, env="VECTOR_DIMENSION")
    VECTOR_DISTANCE: str = Field(default="cosine", env="VECTOR_DISTANCE")
    
    @field_validator("QDRANT_URL")
    @classmethod
    def validate_qdrant_url(cls, v: str) -> str:
        if not v.startswith("http"):
            raise ValueError("Qdrant URL must start with 'http://' or 'https://'")
        return v
    
    # ============================================
    # Rate Limiting & Cost Protection
    # ============================================
    RATE_LIMIT_SESSION: int = 10  # Per session
    RATE_LIMIT_DAILY: int = 100  # Per portfolio per day
    RATE_LIMIT_MONTHLY: int = 2000  # Per portfolio per month
    DAILY_BUDGET_ALERT_THRESHOLD: int = 80  # Alert at 80%
    MONTHLY_BUDGET_ALERT_THRESHOLD: int = 80  # Alert at 80%
    
    # ============================================
    # Caching Configuration
    # ============================================
    CACHE_ENABLED: bool = True
    CACHE_TTL: int = 3600  # 1 hour
    CACHE_MAX_SIZE: int = 1000
    
    # ============================================
    # CORS Configuration
    # ============================================
    ALLOWED_ORIGINS: str = "http://localhost:5173,http://localhost:3000"
    
    @property
    def cors_origins(self) -> List[str]:
        """Parse comma-separated origins into list"""
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]
    
    # ============================================
    # Logging Configuration
    # ============================================
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/app.log"
    LOG_ROTATION: str = "10 MB"
    LOG_RETENTION: str = "7 days"
    
    # ============================================
    # Email Configuration (Optional)
    # ============================================
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: int = 587
    SMTP_USERNAME: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    ALERT_EMAIL: Optional[str] = None
    
    @property
    def email_enabled(self) -> bool:
        """Check if email configuration is complete"""
        return all([
            self.SMTP_HOST,
            self.SMTP_USERNAME,
            self.SMTP_PASSWORD,
            self.ALERT_EMAIL
        ])
    
    # ============================================
    # Multi-Tenant Configuration
    # ============================================
    DEFAULT_PORTFOLIO_ID: Optional[str] = None
    DEFAULT_PORTFOLIO_SUBDOMAIN: str = "demo"
    
    # ============================================
    # Feature Flags
    # ============================================
    ENABLE_ANALYTICS: bool = False
    ENABLE_ADMIN_CMS: bool = False
    ENABLE_BLOG: bool = False
    ENABLE_CONTACT_FORM: bool = False
    
    # ============================================
    # Pydantic Settings Configuration
    # ============================================
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"  # Ignore extra env vars
    )
    
    # ============================================
    # Helper Methods
    # ============================================
    
    def get_qdrant_collection_name(self, portfolio_id: str) -> str:
        """Generate Qdrant collection name for a portfolio"""
        return f"{self.QDRANT_COLLECTION_PREFIX}_{portfolio_id}"
    
    def is_production(self) -> bool:
        """Check if running in production"""
        return self.ENVIRONMENT.lower() == "production"
    
    def is_development(self) -> bool:
        """Check if running in development"""
        return self.ENVIRONMENT.lower() == "development"


# ============================================
# Global Settings Instance
# ============================================

# Create a singleton settings instance
settings = Settings()


# ============================================
# Settings Validation on Import
# ============================================

def validate_settings() -> None:
    """
    Validate critical settings on application startup
    Raises ValueError if any critical setting is invalid
    """
    
    # Check OpenAI configuration
    if not settings.OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY is required")
    
    # Check MongoDB configuration
    if not settings.MONGODB_URL:
        raise ValueError("MONGODB_URL is required")
    
    # Check Qdrant configuration
    if not settings.QDRANT_URL or not settings.QDRANT_API_KEY:
        raise ValueError("Qdrant configuration (URL and API_KEY) is required")
    
    # Check security settings
    if not settings.SECRET_KEY or len(settings.SECRET_KEY) < 32:
        raise ValueError("SECRET_KEY must be at least 32 characters long")
    
    # Warn about production settings
    if settings.is_production():
        if settings.DEBUG:
            print("⚠️  WARNING: DEBUG is enabled in production!")
        if settings.ADMIN_PASSWORD == "change-this-password":
            raise ValueError("Please change the default admin password in production!")
    
    print("✅ Configuration validated successfully")


# ============================================
# Usage Example
# ============================================

if __name__ == "__main__":
    """
    Test configuration loading
    Run: python -m app.core.config
    """
    
    print("=" * 50)
    print("AI Portfolio Platform - Configuration")
    print("=" * 50)
    print(f"App Name: {settings.APP_NAME}")
    print(f"Version: {settings.APP_VERSION}")
    print(f"Environment: {settings.ENVIRONMENT}")
    print(f"Debug Mode: {settings.DEBUG}")
    print()
    print(f"API Host: {settings.API_HOST}:{settings.API_PORT}")
    print()
    print(f"OpenAI Model: {settings.OPENAI_MODEL}")
    print(f"OpenAI API Key: {settings.OPENAI_API_KEY[:10]}...")
    print()
    print(f"MongoDB Database: {settings.MONGODB_DB_NAME}")
    print(f"MongoDB URL: {settings.MONGODB_URL[:30]}...")
    print()
    print(f"Qdrant URL: {settings.QDRANT_URL}")
    print()
    print(f"Rate Limits:")
    print(f"  - Session: {settings.RATE_LIMIT_SESSION} requests")
    print(f"  - Daily: {settings.RATE_LIMIT_DAILY} requests")
    print(f"  - Monthly: {settings.RATE_LIMIT_MONTHLY} requests")
    print()
    print(f"Cache Enabled: {settings.CACHE_ENABLED}")
    print(f"Cache TTL: {settings.CACHE_TTL} seconds")
    print()
    print(f"CORS Origins: {settings.cors_origins}")
    print()
    print(f"Email Alerts Enabled: {settings.email_enabled}")
    print()
    
    # Validate settings
    try:
        validate_settings()
    except ValueError as e:
        print(f"❌ Configuration Error: {e}")