# This file ensures that the tasks module is recognized as a Python package
# and sets up any necessary imports for task modules

# Import task modules here for convenience
# Note: These will be imported by Celery through the configuration

from . import segment_tasks
from . import notification_tasks 
from . import cep_tasks
from . import cdp_tasks
from . import campaign_tasks
from . import analytics_tasks
from . import ab_test_tasks
