"""
Schema models for the WebPush API.
This package provides Pydantic schemas for all data models used in the API.
"""

# Import all schemas for convenience when importing from other modules
from models.schemas.ab_test import *
from models.schemas.analytics import *
from models.schemas.campaign import *
from models.schemas.campaign_template import *
from models.schemas.cdp_integration import *
from models.schemas.cep_decision import *
from models.schemas.notification import *
from models.schemas.permission import *
from models.schemas.role import *
from models.schemas.segment import *
from models.schemas.template import *
from models.schemas.test_variant import *
from models.schemas.trigger import *
from models.schemas.user import *
from models.schemas.webpush import *
from models.schemas.webhook import *
