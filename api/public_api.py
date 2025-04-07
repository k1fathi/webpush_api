from fastapi import APIRouter

from api.v1.endpoints import public

public_api_router = APIRouter()
public_api_router.include_router(public.router, tags=["Public"])
