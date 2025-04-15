from fastapi import APIRouter

from api.v1 import (
    users,
    auth,
    roles,
    permissions,
    campaigns,
    templates,
    segments,
    analytics,
    webhooks,
    notifications,
    ab_test,
    cdp,
    cep,
    triggers,
    webpush
)

api_router = APIRouter()

# Authentication Endpoints
api_router.include_router(auth.router)

# User Management Endpoints
api_router.include_router(users.router)
api_router.include_router(roles.router)
api_router.include_router(permissions.router)

# Campaign Management Endpoints
api_router.include_router(campaigns.router)
api_router.include_router(templates.router)
api_router.include_router(segments.router)
api_router.include_router(ab_test.router)

# Integration Endpoints
api_router.include_router(webhooks.router)
api_router.include_router(cdp.router)
api_router.include_router(cep.router)
api_router.include_router(triggers.router)

# Messaging Endpoints
api_router.include_router(notifications.router)

# Analytics Endpoints
api_router.include_router(analytics.router)

# Web Push Endpoints
api_router.include_router(webpush.router)
