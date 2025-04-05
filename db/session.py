import logging
from typing import AsyncGenerator, Optional, Dict, Any, Generator
from contextlib import asynccontextmanager

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, AsyncEngine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

from core.config import settings

logger = logging.getLogger(__name__)

# Create SQLAlchemy sync engine
engine = create_engine(
    settings.SQLALCHEMY_DATABASE_URI,
    pool_pre_ping=True
)

# Create async engine with correct URI format for asyncpg
# Convert postgresql:// to postgresql+asyncpg:// for async operations
async_uri = settings.SQLALCHEMY_DATABASE_URI
if async_uri.startswith('postgresql://'):
    async_uri = async_uri.replace('postgresql://', 'postgresql+asyncpg://')
elif async_uri.startswith('sqlite://'):
    async_uri = async_uri.replace('sqlite://', 'sqlite+aiosqlite://')

# Create async engine with the modified URI
async_engine = create_async_engine(
    async_uri,
    echo=settings.DB_ECHO_LOG,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
    pool_pre_ping=True,
    pool_recycle=settings.DB_POOL_RECYCLE,
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create async session factory
AsyncSessionLocal = sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# Base class for ORM models
Base = declarative_base()

def get_session() -> Generator[Session, None, None]:
    """
    Get a database session with dependency injection.
    Usage in FastAPI:
        @app.get("/")
        def read_items(db: Session = Depends(get_session)):
            ...
    """
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()

async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """Get an async session for database operations.
    
    This function should be used as a dependency in FastAPI routes.
    
    Yields:
        AsyncSession: An async SQLAlchemy session.
    """
    session = AsyncSessionLocal()
    try:
        yield session
        await session.commit()
    except Exception as e:
        logger.exception("Session rollback due to exception")
        await session.rollback()
        raise
    finally:
        await session.close()

@asynccontextmanager
async def get_async_session_context() -> AsyncGenerator[AsyncSession, None]:
    """Get an async session as an async context manager.
    
    This function should be used in async context managers.
    
    Yields:
        AsyncSession: An async SQLAlchemy session.
    """
    session = AsyncSessionLocal()
    try:
        yield session
        await session.commit()
    except Exception as e:
        logger.exception("Session rollback due to exception")
        await session.rollback()
        raise
    finally:
        await session.close()

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Alias for get_async_session for backward compatibility."""
    async for session in get_async_session():
        yield session

async def close_db_connections() -> None:
    """Close database connections on application shutdown."""
    if isinstance(async_engine, AsyncEngine):
        await async_engine.dispose()
    else:
        async_engine.dispose()
