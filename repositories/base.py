from typing import TypeVar, Generic, Type, List, Optional, Any, Dict, Union
from pydantic import BaseModel
from sqlalchemy.orm import Session

# Define a generic type for SQLAlchemy models
ModelType = TypeVar("ModelType")
# Define a generic type for Pydantic models
SchemaType = TypeVar("SchemaType", bound=BaseModel)

class BaseRepository:
    """Base repository with common CRUD operations"""
    
    def __init__(self, db_session: Optional[Session] = None):
        """Initialize with optional database session"""
        self.db = db_session
    
    def get_db(self) -> Session:
        """Get database session"""
        if self.db is None:
            # This would be implemented in child classes
            # or injected during initialization
            raise NotImplementedError("Database session not provided")
        return self.db

    # In actual implementation, this would have methods like:
    # - create
    # - get
    # - update
    # - delete
    # - list
    # etc.
