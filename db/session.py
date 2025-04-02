from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator

from core.config import settings

# Create SQLAlchemy engine
engine = create_engine(
    settings.SQLALCHEMY_DATABASE_URI,
    pool_pre_ping=True
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

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
