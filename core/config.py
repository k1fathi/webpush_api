from pydantic_settings import BaseSettings
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from contextlib import asynccontextmanager
import logging
from typing import List, AsyncGenerator, Optional
from sqlalchemy.exc import SQLAlchemyError
import asyncpg
from functools import lru_cache
import secrets
from datetime import datetime
import time

logger = logging.getLogger(__name__)

# Base class for SQLAlchemy models
Base = declarative_base()

class Settings(BaseSettings):
    PROJECT_NAME: str = "WebPush API"
    PROJECT_DESCRIPTION: str = "WebPush Notification System API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Server settings
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = True
    WORKERS: int = 1
    
    # Security
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    
    # Database settings
    DATABASE_URL: str = "postgresql+asyncpg://user:password@localhost/webpush_db"
    DB_POOL_SIZE: int = 5
    DB_MAX_OVERFLOW: int = 10
    DB_POOL_TIMEOUT: int = 30
    DB_POOL_RECYCLE: int = 1800
    DB_ECHO: bool = False
    DB_SSL_MODE: str = "prefer"
    
    # Connection retry settings
    DB_MAX_RETRIES: int = 5
    DB_RETRY_DELAY: int = 5
    
    # CORS
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",  # Frontend
        "http://localhost:8000",  # Backend
    ]
    
    class Config:
        env_file = ".env"

settings = Settings()

class DatabaseManager:
    def __init__(self):
        self.engine = None
        self.async_session_maker = None

    async def init_db(self) -> None:
        """Initialize database connection"""
        try:
            self.engine = create_async_engine(
                settings.DATABASE_URL,
                echo=settings.DB_ECHO,
                pool_size=settings.DB_POOL_SIZE,
                max_overflow=settings.DB_MAX_OVERFLOW,
                pool_timeout=settings.DB_POOL_TIMEOUT,
                pool_recycle=settings.DB_POOL_RECYCLE,
                pool_pre_ping=True,
            )
            
            self.async_session_maker = async_sessionmaker(
                self.engine,
                class_=AsyncSession,
                expire_on_commit=False,
                autocommit=False,
                autoflush=False
            )

            # Verify connection
            async with self.engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
                
            logger.info("Database connection established successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize database: {str(e)}")
            raise

    async def close_db(self) -> None:
        """Close database connection"""
        if self.engine:
            await self.engine.dispose()
            logger.info("Database connection closed")

    @asynccontextmanager
    async def get_db(self) -> AsyncGenerator[AsyncSession, None]:
        """Get database session"""
        if not self.async_session_maker:
            await self.init_db()
            
        async with self.async_session_maker() as session:
            try:
                yield session
            except SQLAlchemyError as e:
                await session.rollback()
                logger.error(f"Database error: {str(e)}")
                raise
            finally:
                await session.close()

    async def check_connection(self) -> bool:
        """Check database connection health"""
        try:
            async with self.get_db() as db:
                await db.execute("SELECT 1")
            return True
        except Exception as e:
            logger.error(f"Database health check failed: {str(e)}")
            return False

    @staticmethod
    @lru_cache()
    def get_instance() -> 'DatabaseManager':
        """Get singleton instance of DatabaseManager"""
        return DatabaseManager()

# Create singleton instance
db_manager = DatabaseManager.get_instance()

# FastAPI dependency
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with db_manager.get_db() as session:
        yield session

# Helper functions
async def execute_query(query, params: Optional[dict] = None) -> list:
    async with db_manager.get_db() as session:
        result = await session.execute(query, params)
        return result.fetchall()
