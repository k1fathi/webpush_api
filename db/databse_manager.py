from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from contextlib import asynccontextmanager
from core.config import settings
import logging
from typing import AsyncGenerator, Optional
from sqlalchemy.exc import SQLAlchemyError
import asyncpg
from functools import lru_cache

logger = logging.getLogger(__name__)

# Base class for SQLAlchemy models
Base = declarative_base()

class DatabaseConfig:
    def __init__(self):
        self.engine = None
        self.async_session_maker = None

    async def init_db(self) -> None:
        """Initialize database connection"""
        try:
            self.engine = create_async_engine(
                settings.DATABASE_URL,
                echo=settings.DEBUG,
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
    def get_instance() -> 'DatabaseConfig':
        """Get singleton instance of DatabaseConfig"""
        return DatabaseConfig()

# Create singleton instance
db_config = DatabaseConfig.get_instance()

# Dependency for FastAPI
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with db_config.get_db() as session:
        yield session

# Helper functions for common database operations
async def execute_query(query, params: Optional[dict] = None) -> list:
    """Execute raw SQL query"""
    async with db_config.get_db() as session:
        result = await session.execute(query, params)
        return result.fetchall()

async def health_check() -> dict:
    """Comprehensive database health check"""
    try:
        start_time = time.time()
        connection_ok = await db_config.check_connection()
        response_time = time.time() - start_time
        
        return {
            "status": "healthy" if connection_ok else "unhealthy",
            "response_time_ms": round(response_time * 1000, 2),
            "connection_pool": {
                "size": settings.DB_POOL_SIZE,
                "overflow": settings.DB_MAX_OVERFLOW
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }
