from celery import Celery
from config import settings

celery_app = Celery('webpush_worker')

celery_app.conf.update(
    broker_url=settings.RABBITMQ_URL,
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
)

# Import tasks module after Celery app initialization
import tasks  # noqa
