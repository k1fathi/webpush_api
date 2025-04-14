import logging
import os
from contextlib import asynccontextmanager
import uvicorn
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.openapi.docs import get_swagger_ui_html, get_redoc_html
from fastapi.openapi.utils import get_openapi

from api.v1.router import api_router
from core.config import settings
from core.exceptions.handlers import register_exception_handlers
from core.logging.config import configure_logging
from core.db import init_db, create_tables
from services.user import UserService

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
            
            # Ensure admin user exists
            user_service = UserService()
            await user_service.ensure_admin_user()
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
    docs_url=None,  # We'll define custom routes for docs
    redoc_url=None,  # We'll define custom routes for redoc
    openapi_url="/openapi.json",  # Remove the API prefix for easier access
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

# Root endpoint - Return info instead of redirecting
@app.get("/", include_in_schema=False)
def read_root():
    return {"message": "Webpush API is running", "docs_url": "/docs", "redoc_url": "/redoc"}

# Custom Swagger UI route that works in all environments
@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url="/openapi.json",  # Updated to match the openapi_url in FastAPI app
        title=f"{settings.PROJECT_NAME} - Swagger UI",
        oauth2_redirect_url=None,
        swagger_js_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.9.0/swagger-ui-bundle.js",
        swagger_css_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.9.0/swagger-ui.css",
    )

# Custom ReDoc route that works in all environments
@app.get("/redoc", include_in_schema=False)
async def custom_redoc_html():
    return get_redoc_html(
        openapi_url="/openapi.json",  # Updated to match the openapi_url in FastAPI app
        title=f"{settings.PROJECT_NAME} - ReDoc",
        redoc_js_url="https://cdn.jsdelivr.net/npm/redoc@2.0.0/bundles/redoc.standalone.js",
    )

# Mount static files directory with better error handling
static_dir = "static"
try:
    # Create static directory if it doesn't exist
    if not os.path.exists(static_dir):
        logger.warning(f"Static directory '{static_dir}' not found. Creating it...")
        os.makedirs(static_dir, exist_ok=True)
        # Create a placeholder file to ensure the directory isn't empty
        with open(os.path.join(static_dir, "placeholder.txt"), "w") as f:
            f.write("This is a placeholder file for the static directory")
    
    app.mount("/static", StaticFiles(directory=static_dir), name="static")
    logger.info(f"Successfully mounted static files from '{static_dir}'")
except Exception as e:
    logger.error(f"Failed to mount static directory: {e}")
    logger.warning("Static file serving will be disabled. This may affect UI components.")

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
