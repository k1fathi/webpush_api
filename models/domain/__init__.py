"""
Domain models for SQLAlchemy ORM
"""

# Import all model classes for easier imports elsewhere

from .ab_test import AbTestModel
from .analytics import AnalyticsModel
from .campaign import CampaignModel
from .campaign_template import CampaignTemplateModel
from .cdp_integration import CdpIntegrationModel
from .cep_decision import CepDecisionModel
from .notification import NotificationModel
from .permission import PermissionModel
from .role import RoleModel
from .segment import SegmentModel
from .template import TemplateModel, TemplateVersionModel
from .test_variant import TestVariantModel
from .trigger import TriggerModel, TriggerExecutionModel
from .user import UserModel

# Note: UserRoleModel and RolePermissionModel have been removed in favor of 
# using the association tables directly (user_role and role_permission)
