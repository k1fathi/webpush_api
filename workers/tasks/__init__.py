# This file ensures that the tasks module is recognized as a Python package

import logging
import sys

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Helper function to safely import modules
def safe_import(module_name):
    try:
        module = __import__(f"{__package__}.{module_name}", fromlist=['*'])
        logger.info(f"Successfully imported {module_name}")
        return module
    except ImportError as e:
        logger.warning(f"Could not import {module_name}: {e}")
        return None

# Try to safely import all task modules
try:
    # Instead of direct imports that can fail and stop execution,
    # conditionally import and continue regardless of failures
    segment_module = safe_import('segment_tasks')
    notification_module = safe_import('notification_tasks')
    cep_module = safe_import('cep_tasks')
    cdp_module = safe_import('cdp_tasks')
    campaign_module = safe_import('campaign_tasks')
    analytics_module = safe_import('analytics_tasks')
    ab_test_module = safe_import('ab_test_tasks')
    
    logger.info("Task modules loaded")
    
except Exception as e:
    logger.error(f"Error during task module imports: {e}")
