import os
from celery import Celery
from core.config import settings

# Configure Celery app
celery_app = Celery(
    "webpush_workers",
    broker=f"amqp://{settings.RABBITMQ_USER}:{settings.RABBITMQ_PASSWORD}@{settings.RABBITMQ_HOST}:5672/",
    backend=f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/0"
)

# Load tasks module
celery_app.conf.imports = [
    "workers.tasks"
]

# Configure queues and routing
celery_app.conf.task_routes = {
    "deliver_notification": {"queue": "notifications"},
    "expired_subscription": {"queue": "maintenance"},
}

# Set up task result expiration
celery_app.conf.result_expires = 3600  # 1 hour

# Configure retry settings
celery_app.conf.task_acks_late = True
celery_app.conf.task_reject_on_worker_lost = True

# Configure logging
celery_app.conf.worker_log_format = "[%(asctime)s: %(levelname)s/%(processName)s] %(message)s"