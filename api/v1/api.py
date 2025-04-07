from fastapi import APIRouter

from api.v1.endpoints import (
    users, 
    auth, 
    roles, 
    notifications, 
    campaigns, 
    segments, 
    templates,
    subscriptions,
    subscription_management,
    segment_management,
    template_management,
    campaign_management, # Add this import
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
api_router.include_router(subscriptions.router, prefix="/subscriptions/status", tags=["Subscription Status"])
api_router.include_router(subscription_management.router, prefix="/subscriptions", tags=["Subscription Management"])
api_router.include_router(segment_management.router, prefix="/segments", tags=["Segment Management"])
api_router.include_router(template_management.router, prefix="/templates", tags=["Template Management"])
api_router.include_router(campaign_management.router, prefix="/campaigns", tags=["Campaign Management"]) # Add this line
api_router.include_router(analytics.router, prefix="/analytics", tags=["Analytics"])
