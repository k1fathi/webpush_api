from fastapi import APIRouter

from api.v1.endpoints import (
    users, 
    auth, 
    roles, 
    notifications, 
    campaigns, 
    segments, 
    templates,
    subscriptions,  # Add this import
    analytics
)

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(roles.router, prefix="/roles", tags=["Roles"])
api_router.include_router(notifications.router, prefix="/notifications", tags=["Notifications"])
api_router.include_router(campaigns.router, prefix="/campaigns", tags=["Campaigns"])
api_router.include_router(segments.router, prefix="/segments", tags=["Segments"])
api_router.include_router(templates.router, prefix="/templates", tags=["Templates"])
api_router.include_router(subscriptions.router, prefix="/subscriptions", tags=["Subscriptions"])  # Add this line
api_router.include_router(analytics.router, prefix="/analytics", tags=["Analytics"])
