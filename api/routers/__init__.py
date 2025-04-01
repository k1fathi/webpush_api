from fastapi import APIRouter

# Import routers with consistent suffix naming
from .user_router import router as user_router
from .webpush_router import router as webpush_router
from .campaign_router import router as campaign_router
from .analytics_router import router as analytics_router
from .segment_router import router as segment_router
from .trigger_router import router as trigger_router
from .template_router import router as template_router

# Create main router
api_router = APIRouter()

# Include all routers with their prefixes
routers = [
    (user_router, "/users", "users"),
    (webpush_router, "/webpush", "webpush"),
    (campaign_router, "/campaigns", "campaigns"),
    (analytics_router, "/analytics", "analytics"),
    (segment_router, "/segments", "segments"),
    (trigger_router, "/triggers", "triggers"),
    (template_router, "/templates", "templates"),
]

# Register all routers
for router, prefix, tag in routers:
    api_router.include_router(
        router,
        prefix=prefix,
        tags=[tag]
    )
