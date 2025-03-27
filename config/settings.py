from pydantic import BaseModel
from typing import Optional, List

class Settings(BaseModel):
    # API Settings
    API_HOST: str = "57.129.71.50"
    API_PORT: int = 8000
    API_WORKERS: int = 4
    DEBUG: bool = False
    ALLOWED_HOSTS: List[str] = ["*"]
    
    # Database Settings
    POSTGRES_USER: str = "webpush_user"
    POSTGRES_PASSWORD: str = "webpush_password"
    POSTGRES_DB: str = "webpush_db"
    POSTGRES_HOST: str = "db"
    POSTGRES_PORT: int = 5432
    DATABASE_URL: Optional[str] = None

    # RabbitMQ Settings
    RABBITMQ_HOST: str = "rabbitmq"
    RABBITMQ_PORT: int = 5672
    RABBITMQ_USER: str = "guest"
    RABBITMQ_PASS: str = "guest"

    # Redis Settings
    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379

    def __init__(self, **data):
        super().__init__(**data)
        if not self.DATABASE_URL:
            self.DATABASE_URL = f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
