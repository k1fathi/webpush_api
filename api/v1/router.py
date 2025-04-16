from fastapi import APIRouter

from .users import router as users_router
from .auth import router as auth_router
from .roles import router as roles_router
from .permissions import router as permissions_router
from .campaigns import router as campaigns_router
from .templates import router as templates_router
from .segments import router as segments_router
from .analytics import router as analytics_router
from .webhooks import router as webhooks_router
from .notifications import router as notifications_router
from .ab_test import router as ab_test_router
from .cdp import router as cdp_router
from .cep import router as cep_router
from .triggers import router as triggers_router
from .webpush import router as webpush_router

api_router = APIRouter()

api_router.include_router(auth_router)
api_router.include_router(users_router)
api_router.include_router(roles_router)
api_router.include_router(permissions_router)
api_router.include_router(campaigns_router)
api_router.include_router(templates_router)
api_router.include_router(segments_router)
api_router.include_router(ab_test_router)
api_router.include_router(webhooks_router)
api_router.include_router(cdp_router)
api_router.include_router(cep_router)
api_router.include_router(triggers_router)
api_router.include_router(notifications_router)
api_router.include_router(analytics_router)
api_router.include_router(webpush_router)

