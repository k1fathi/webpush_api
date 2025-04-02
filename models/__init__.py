# Basic model initialization - reducing dependencies
# Previously: from .user import User

# Import these explicitly only when needed to avoid circular imports
from .segment import Segment
from .template import Template
from .campaign import Campaign
from .notification import Notification
from .webhook import Webhook
from .trigger import Trigger
from .ab_test import AbTest
from .test_variant import TestVariant
from .analytics import Analytics
from .cdp_integration import CdpIntegration
from .cep_decision import CepDecision

__all__ = [
    'Segment',
    'Template',
    'Campaign',
    'Notification',
    'Webhook',
    'Trigger',
    'AbTest',
    'TestVariant',
    'Analytics',
    'CdpIntegration',
    'CepDecision',
]
