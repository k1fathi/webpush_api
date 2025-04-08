from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from db.session import get_db

router = APIRouter()

@router.get("/", status_code=status.HTTP_200_OK)
async def health_check(db: AsyncSession = Depends(get_db)):
    """
    Health check endpoint to verify API is running and database connection is working
    """
    try:
        # Use SQLAlchemy's text() function for raw SQL
        await db.execute(text("SELECT 1"))
        return {
            "status": "ok",
            "message": "Service is running",
            "database_connection": True
        }
    except Exception as e:
        return {
            "status": "degraded",
            "message": "Service is running but database connection failed",
            "database_connection": False,
            "error": str(e)
        }
