from celery import Celery
import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    from core.config import settings
    # Configure using imported settings
    celery_app = Celery(
        "webpush_workers",
        broker=f"amqp://{settings.RABBITMQ_USER}:{settings.RABBITMQ_PASSWORD}@{settings.RABBITMQ_HOST}:5672/",
        backend=f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/0"
    )
except ImportError:
    # Fallback to environment variables
    logger.warning("Failed to import settings, using environment variables")
    celery_app = Celery(
        "webpush_workers",
        broker=f"amqp://{os.environ.get('RABBITMQ_USER', 'guest')}:{os.environ.get('RABBITMQ_PASSWORD', 'guest')}@{os.environ.get('RABBITMQ_HOST', 'rabbitmq')}:5672/",
        backend=f"redis://{os.environ.get('REDIS_HOST', 'redis')}:{os.environ.get('REDIS_PORT', '6379')}/0"
    )

# Basic celery configuration
celery_app.conf.imports = [
    "workers.tasks.segment_tasks",
    "workers.tasks.notification_tasks",
    # Temporarily comment out problematic imports until they're fixed
    # "workers.tasks.cep_tasks", 
    # "workers.tasks.cdp_tasks",
    "workers.tasks.campaign_tasks"
    # "workers.tasks.analytics_tasks",
    # "workers.tasks.ab_test_tasks"
]

# Configure queues and routing
celery_app.conf.task_routes = {
    "workers.tasks.notification_tasks.process_pending_notifications": {"queue": "notifications"},
    "workers.tasks.notification_tasks.send_notification": {"queue": "notifications"},
    "workers.tasks.campaign_tasks.execute_campaign": {"queue": "campaigns"},
    "workers.tasks.segment_tasks.evaluate_segment": {"queue": "segments"}
}

# Set up task result expiration
celery_app.conf.result_expires = 3600  # 1 hour

# Configure retry settings
celery_app.conf.task_acks_late = True
celery_app.conf.task_reject_on_worker_lost = True

# Configure logging
celery_app.conf.worker_log_format = "[%(asctime)s: %(levelname)s/%(processName)s] %(message)s"

# Silence warnings about missing imports
celery_app.conf.worker_hijack_root_logger = False
celery_app.conf.worker_log_color = False
