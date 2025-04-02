import os
import secrets
from typing import Any, Dict, List, Optional, Union

# Determine Pydantic version and import appropriate modules
try:
    import pydantic
    pydantic_version = int(pydantic.__version__.split('.')[0])
    
    if pydantic_version >= 2:
        # For Pydantic v2.x
        from pydantic import AnyHttpUrl, PostgresDsn, field_validator
        from pydantic_settings import BaseSettings
        
        USING_V2 = True
    else:
        # For Pydantic v1.x
        from pydantic import AnyHttpUrl, BaseSettings, PostgresDsn, validator
        
        USING_V2 = False
except ImportError:
    # Fall back to basic settings if pydantic is not available
    import sys
    print("Error: Unable to import required Pydantic modules. Check your installation.")
    sys.exit(1)

class Settings(BaseSettings):
    # API settings
    API_PREFIX: str = "/api"
    PROJECT_NAME: str = "WebPush API"
    
    # CORS
    CORS_ORIGINS: List[str] = ["*"]
    
    # Security
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    
    # Database
    POSTGRES_SERVER: str = os.environ.get("POSTGRES_SERVER", "db")
    POSTGRES_USER: str = os.environ.get("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD: str = os.environ.get("POSTGRES_PASSWORD", "postgres")
    POSTGRES_DB: str = os.environ.get("POSTGRES_DB", "webpush")
    POSTGRES_PORT: str = os.environ.get("POSTGRES_PORT", "5432")
    SQLALCHEMY_DATABASE_URI: Optional[PostgresDsn] = None

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

    # Configure with the appropriate Config class based on Pydantic version
    if USING_V2:
        model_config = {
            "case_sensitive": True,
            "env_file": ".env"
        }
    else:
        class Config:
            case_sensitive = True
            env_file = ".env"


# Define the validator outside the class definition to avoid syntax errors
if USING_V2:
    @field_validator("SQLALCHEMY_DATABASE_URI", mode="before")
    def assemble_db_connection_v2(cls, v: Optional[str], info) -> Any:
        if isinstance(v, str):
            return v
        values = info.data
        return PostgresDsn.build(
            scheme="postgresql",
            username=values.get("POSTGRES_USER"),
            password=values.get("POSTGRES_PASSWORD"),
            host=values.get("POSTGRES_SERVER"),
            path=f"/{values.get('POSTGRES_DB') or ''}",
        )
    
    # Add the validator to the class
    setattr(Settings, "assemble_db_connection", assemble_db_connection_v2)
else:
    @validator("SQLALCHEMY_DATABASE_URI", pre=True)
    def assemble_db_connection_v1(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        if isinstance(v, str):
            return v
        return PostgresDsn.build(
            scheme="postgresql",
            user=values.get("POSTGRES_USER"),
            password=values.get("POSTGRES_PASSWORD"),
            host=values.get("POSTGRES_SERVER"),
            path=f"/{values.get('POSTGRES_DB') or ''}",
        )
    
    # Add the validator to the class
    setattr(Settings, "assemble_db_connection", assemble_db_connection_v1)

# Initialize settings
settings = Settings()

