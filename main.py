import logging
from contextlib import asynccontextmanager
import uvicorn
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from api.v1.router import api_router
from core.config import settings
from core.exceptions.handlers import register_exception_handlers
from core.logging.config import configure_logging
from core.db import init_db, create_tables

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Database initialization and validation
    try:
        db_init_success = False
        try:
            await init_db()
            db_init_success = True
            logger.info("Database initialized and validated successfully")
        except Exception as e:
            logger.warning(f"Database validation failed: {e}")
            
            if settings.AUTO_CREATE_TABLES:
                logger.info("Attempting to create missing tables")
                try:
                    await create_tables()
                    # Try to initialize the DB again after creating tables
                    await init_db()
                    db_init_success = True
                    logger.info("Successfully created missing tables and initialized database")
                except Exception as table_error:
                    logger.error(f"Failed to create tables: {table_error}")
                    raise
            else:
                logger.error("AUTO_CREATE_TABLES is disabled. Not creating missing tables.")
                raise
        
        if db_init_success:
            logger.info("Database setup complete")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise
    
    yield
    
    # Cleanup (if needed)
    logger.info("Shutting down application")

# Create FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="WebPush Notification API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url=f"{settings.API_PREFIX}/openapi.json",
    lifespan=lifespan,
)

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
configure_logging()

# Register exception handlers
register_exception_handlers(app)

# Include API router
app.include_router(api_router, prefix=settings.API_PREFIX)

# Redirect root path to Swagger docs
@app.get("/", include_in_schema=False)
def redirect_to_docs():
    return RedirectResponse(url="/docs")

# Health check endpoint
@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run("main:app", host=settings.API_HOST, port=8000)

# filepath: c:\K1\ZUZZUU\webpush\webpush_api\api\deps.py
from fastapi import Depends, HTTPException, status
from models.domain.user import UserModel
from services.user import UserService

async def get_current_active_user(
    user_service: UserService = Depends(),
    token: str = Depends()  # Replace with actual token dependency
) -> UserModel:
    """
    Dependency to get the current active user based on the provided token.
    """
    user = await user_service.get_user_by_token(token)
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or inactive user",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user
