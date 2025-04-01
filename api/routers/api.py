from fastapi import APIRouter
from api.routers import user_router
from api.v1.endpoints import webpush_endpoint
from api.v1.endpoints import campaign_endpoint
from api.v1.endpoints import analytics_endpoint
from api.v1.endpoints import trigger_endpoint

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(user_router.router, tags=["users"])
api_router.include_router(webpush_endpoint.router, prefix="/webpush", tags=["webpush"])
api_router.include_router(campaign_endpoint.router, prefix="/campaigns", tags=["campaigns"])
api_router.include_router(analytics_endpoint.router, prefix="/analytics", tags=["analytics"])
api_router.include_router(trigger_endpoint.router, prefix="/triggers", tags=["triggers"])
