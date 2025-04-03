import os
import secrets
from typing import Any, Dict, List, Optional, Union

# Update imports for Pydantic v2
from pydantic import AnyHttpUrl, field_validator, PostgresDsn, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # API settings
    API_PREFIX: str = "/api"
    PROJECT_NAME: str = "WebPush API"
    API_HOST: str = "localhost"  # Add the API_HOST field that's in the .env file
    
    # CORS - Fix parsing for CORS_ORIGINS
    CORS_ORIGINS: Union[List[str], str] = "*"
    
    # Security
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    
    # Database - Update to use PostgreSQL user for both username and DB name
    POSTGRES_SERVER: str = os.environ.get("POSTGRES_SERVER", "")
    POSTGRES_USER: str = os.environ.get("POSTGRES_USER", "")
    POSTGRES_PASSWORD: str = os.environ.get("POSTGRES_PASSWORD", "")
    POSTGRES_DB: str = os.environ.get("POSTGRES_DB", "")
    POSTGRES_PORT: str = os.environ.get("POSTGRES_PORT", "")
    SQLALCHEMY_DATABASE_URI: str | PostgresDsn = None

    # Redis
    REDIS_HOST: str = os.environ.get("REDIS_HOST", "redis")
    REDIS_PORT: int = int(os.environ.get("REDIS_PORT", 6379))

    # RabbitMQ
    RABBITMQ_HOST: str = os.environ.get("RABBITMQ_HOST", "rabbitmq")
    RABBITMQ_USER: str = os.environ.get("RABBITMQ_USER", "guest")
    RABBITMQ_PASSWORD: str = os.environ.get("RABBITMQ_PASSWORD", "guest")
    
    # WebPush settings
    VAPID_PRIVATE_KEY: str = os.environ.get("VAPID_PRIVATE_KEY", "")
    VAPID_PUBLIC_KEY: str = os.environ.get("VAPID_PUBLIC_KEY", "")
    VAPID_CLAIMS_EMAIL: str = os.environ.get("VAPID_CLAIMS_EMAIL", "mailto:admin@example.com")
    
    # CDP Integration
    CDP_API_URL: Optional[str] = os.environ.get("CDP_API_URL")
    CDP_API_KEY: Optional[str] = os.environ.get("CDP_API_KEY")
    
    # CEP Integration
    CEP_API_URL: Optional[str] = os.environ.get("CEP_API_URL")
    CEP_API_KEY: Optional[str] = os.environ.get("CEP_API_KEY")

    # Logging
    LOG_LEVEL: str = os.environ.get("LOG_LEVEL", "INFO")
    LOG_FORMAT: str = os.environ.get("LOG_FORMAT", "json")

    # Add validator for CORS_ORIGINS to handle string to list conversion
    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            if v == "*":
                # Return as-is for the wildcard case
                return v
            # Split by comma for multiple origins
            return [origin.strip() for origin in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError("CORS_ORIGINS should be a string or list")

    # Updated for Pydantic v2
    @model_validator(mode="before")
    @classmethod
    def assemble_db_connection(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        if values.get("SQLALCHEMY_DATABASE_URI"):
            return values
        
        # Convert port to int for PostgresDsn.build
        port = values.get("POSTGRES_PORT")
        if port and isinstance(port, str):
            try:
                port = int(port)
            except ValueError:
                port = 5432  # Default to 5432 if conversion fails
        
        # Build connection string with port as integer
        # IMPORTANT CHANGE: Remove the leading slash in the path
        db_url = PostgresDsn.build(
            scheme="postgresql",
            username=values.get("POSTGRES_USER"),
            password=values.get("POSTGRES_PASSWORD"),
            host=values.get("POSTGRES_SERVER"),
            path=f"{values.get('POSTGRES_DB') or ''}",  # Remove the leading slash here
            port=port,
        )
        values["SQLALCHEMY_DATABASE_URI"] = db_url
        return values

    # Replace Config class with model_config
    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",  # Add this to ignore extra fields from .env
    )

settings = Settings()

# Ensure SQLALCHEMY_DATABASE_URI is a string
settings.SQLALCHEMY_DATABASE_URI = str(settings.SQLALCHEMY_DATABASE_URI)

