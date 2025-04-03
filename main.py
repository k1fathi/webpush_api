import uvicorn
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from api.v1.router import api_router
from core.config import settings
from core.exceptions.handlers import register_exception_handlers
from core.logging.config import configure_logging

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="WebPush Notification API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
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
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

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
