import os
import sys

try:
    # Import the celery app from the central module
    from core.celery_app import celery_app
except ImportError as e:
    print(f"Error importing celery_app: {e}")
    # Fall back to using environment variables if import fails
    from celery import Celery
    
    # Create a minimal setup for Celery
    print("Warning: Failed to import settings from core.config, using environment variables as fallback")
    
    celery_app = Celery(
        "webpush_workers",
        broker=f"amqp://{os.environ.get('RABBITMQ_USER', 'guest')}:{os.environ.get('RABBITMQ_PASSWORD', 'guest')}@{os.environ.get('RABBITMQ_HOST', 'localhost')}:5672/",
        backend=f"redis://{os.environ.get('REDIS_HOST', 'localhost')}:{os.environ.get('REDIS_PORT', '6379')}/0"
    )
    
    # Minimum configuration to get the worker running
    celery_app.conf.imports = [
        "workers.tasks.segment_tasks",
        "workers.tasks.notification_tasks",
        "workers.tasks.cep_tasks", 
        "workers.tasks.cdp_tasks",
        "workers.tasks.campaign_tasks",
        "workers.tasks.analytics_tasks",
        "workers.tasks.ab_test_tasks"
    ]

# This file is only needed to provide the entrypoint for the Celery worker
# All configuration is centralized in core.celery_app