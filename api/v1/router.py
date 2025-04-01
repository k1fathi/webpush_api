from fastapi import APIRouter

from .endpoints import ab_tests, analytics, campaigns, cdps, ceps, permissions, roles, segments, templates, triggers, users, webhooks, webpush

api_router = APIRouter()

api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(roles.router, prefix="/roles", tags=["roles"])
api_router.include_router(permissions.router, prefix="/permissions", tags=["permissions"])
api_router.include_router(segments.router, prefix="/segments", tags=["segments"])
api_router.include_router(templates.router, prefix="/templates", tags=["templates"])
api_router.include_router(campaigns.router, prefix="/campaigns", tags=["campaigns"])
api_router.include_router(ab_tests.router, prefix="/ab-tests", tags=["ab-tests"])  # Add the A/B tests router
api_router.include_router(triggers.router, prefix="/triggers", tags=["triggers"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
api_router.include_router(webhooks.router, prefix="/webhooks", tags=["webhooks"])
api_router.include_router(cdps.router, prefix="/cdp", tags=["cdp"])
api_router.include_router(ceps.router, prefix="/cep", tags=["cep"])
api_router.include_router(webpush.router, prefix="/webpush", tags=["webpush"])
