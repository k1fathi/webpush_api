import os
from celery import Celery

# Import settings with try-except to handle Pydantic version differences
try:
    from core.config import settings
except ImportError:
    # Fall back to using environment variables if settings import fails
    import sys
    print("Warning: Failed to import settings from core.config, using environment variables as fallback")
    
    # Create a minimal settings object that mimics the required attributes
    class MinimalSettings:
        RABBITMQ_USER = os.environ.get('RABBITMQ_USER', 'guest')
        RABBITMQ_PASSWORD = os.environ.get('RABBITMQ_PASSWORD', 'guest')
        RABBITMQ_HOST = os.environ.get('RABBITMQ_HOST', 'localhost')
        REDIS_HOST = os.environ.get('REDIS_HOST', 'localhost')
        REDIS_PORT = os.environ.get('REDIS_PORT', '6379')
    
    settings = MinimalSettings()

# Configure Celery app
celery_app = Celery(
    "webpush_workers",
    broker=f"amqp://{settings.RABBITMQ_USER}:{settings.RABBITMQ_PASSWORD}@{settings.RABBITMQ_HOST}:5672/",
    backend=f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/0"
)

# Load tasks module using absolute imports to ensure all tasks are discovered
celery_app.conf.imports = [
    "workers.tasks.segment_tasks",
    "workers.tasks.notification_tasks",
    "workers.tasks.cep_tasks", 
    "workers.tasks.cdp_tasks",
    "workers.tasks.campaign_tasks",
    "workers.tasks.analytics_tasks",
    "workers.tasks.ab_test_tasks"
]

# Configure queues and routing
celery_app.conf.task_routes = {
    "workers.tasks.notification_tasks.process_pending_notifications": {"queue": "notifications"},
    "workers.tasks.notification_tasks.send_notification": {"queue": "notifications"},
    "workers.tasks.campaign_tasks.execute_campaign": {"queue": "campaigns"},
    "workers.tasks.segment_tasks.evaluate_segment": {"queue": "segments"},
    "workers.tasks.ab_test_tasks.analyze_ab_test": {"queue": "analytics"},
    # Add more specific routing as needed
}

# Set up task result expiration
celery_app.conf.result_expires = 3600  # 1 hour

# Configure retry settings
celery_app.conf.task_acks_late = True
celery_app.conf.task_reject_on_worker_lost = True

# Configure logging
celery_app.conf.worker_log_format = "[%(asctime)s: %(levelname)s/%(processName)s] %(message)s"