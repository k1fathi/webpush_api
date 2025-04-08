from fastapi import APIRouter

from .endpoints import (
    users,
    campaigns,
    segments,
    templates,
    webhooks,
    notifications,
    ab_tests,
    analytics,
    triggers,
    external_auth,
    health  # Now this import will work
)

# Define the API router
api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(campaigns.router, prefix="/campaigns", tags=["campaigns"])
api_router.include_router(segments.router, prefix="/segments", tags=["segments"])
api_router.include_router(templates.router, prefix="/templates", tags=["templates"])
api_router.include_router(webhooks.router, prefix="/webhooks", tags=["webhooks"])
api_router.include_router(notifications.router, prefix="/notifications", tags=["notifications"])
api_router.include_router(ab_tests.router, prefix="/ab-tests", tags=["ab-tests"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
api_router.include_router(triggers.router, prefix="/triggers", tags=["triggers"])
api_router.include_router(external_auth.router, prefix="/external-auth", tags=["external-auth"])
api_router.include_router(health.router, prefix="/health", tags=["health"])

