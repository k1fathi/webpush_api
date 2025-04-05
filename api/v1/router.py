from fastapi import APIRouter

from .endpoints import ab_tests, analytics, campaigns, cdps, ceps, permissions, roles, segments
from .endpoints import templates, triggers, users, webhooks, webpush, notification_delivery
from .endpoints import notifications, segment_execution  # Add segment execution
from .endpoints import campaign_templates

api_router = APIRouter()

# Endpoints for Users
#api_router.include_router(users.router, prefix="/users", tags=["users"])

# Endpoints for Roles
#api_router.include_router(roles.router, prefix="/roles", tags=["roles"])

# Endpoints for Permissions
#api_router.include_router(permissions.router, prefix="/permissions", tags=["permissions"])

# Endpoints for Segments
#api_router.include_router(segments.router, prefix="/segments", tags=["segments"])
#api_router.include_router(segment_execution.router, prefix="/segment-execution", tags=["segment-execution"])

# Endpoints for Templates
#api_router.include_router(templates.router, prefix="/templates", tags=["templates"])

# Endpoints for Campaigns
#api_router.include_router(campaigns.router, prefix="/campaigns", tags=["campaigns"])

# Endpoints for A/B Testing
#api_router.include_router(ab_tests.router, prefix="/ab-tests", tags=["ab-tests"])

# Endpoints for Triggers
#api_router.include_router(triggers.router, prefix="/triggers", tags=["triggers"])

# Endpoints for Analytics
#api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])

# Endpoints for Webhooks
#api_router.include_router(webhooks.router, prefix="/webhooks", tags=["webhooks"])

# Endpoints for CDP Integration
#api_router.include_router(cdps.router, prefix="/cdp", tags=["cdp"])

# Endpoints for CEP (Customer Engagement Platform)
#api_router.include_router(ceps.router, prefix="/cep", tags=["cep"])

# Endpoints for Webpush
#api_router.include_router(webpush.router, prefix="/webpush", tags=["webpush"])

# Endpoints for Notification Delivery
#api_router.include_router(notification_delivery.router, prefix="/delivery", tags=["delivery"])

# Endpoints for Notifications
#api_router.include_router(notifications.router, prefix="/notifications", tags=["notifications"])

# Endpoints for Campaign Templates
#api_router.include_router(campaign_templates.router, prefix="/campaign-templates", tags=["campaign templates"])
