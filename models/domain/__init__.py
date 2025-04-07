"""
Domain models for SQLAlchemy ORM
"""

# Import models to ensure they are registered with the ORM before relationships are accessed
from models.domain.user import UserModel, user_role, user_segment
from models.domain.role import RoleModel, role_permission
from models.domain.permission import PermissionModel
from models.domain.segment import SegmentModel
from models.domain.notification import NotificationModel
from models.domain.template import TemplateModel, TemplateVersionModel
from models.domain.ab_test import AbTestModel
from models.domain.test_variant import TestVariantModel
from models.domain.campaign import CampaignModel
from models.domain.campaign_template import CampaignTemplateModel
from models.domain.analytics import AnalyticsModel
from models.domain.cep_decision import CepDecisionModel
from models.domain.cdp_integration import CdpIntegrationModel
from models.domain.trigger import TriggerModel, TriggerExecutionModel
