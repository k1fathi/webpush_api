from celery import Celery
from config.settings import settings

celery_app = Celery(
    "webpush_worker",
    broker=settings.RABBITMQ_URL,
    include=['workers.tasks']
)

# Update Celery configuration
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_routes={
        'tasks.process_notification': {'queue': 'notifications'}
    },
    task_default_queue='notifications',
    broker_connection_retry_on_startup=True,
    worker_prefetch_multiplier=1,
    task_acks_late=True
)

# Make sure this is at the end of the file
if __name__ == '__main__':
    celery_app.start()

# Import tasks module after Celery app initialization
from workers import tasks  # noqa
