from celery import Celery
from config.settings import settings

celery_app = Celery(
    "webpush_worker",
    broker=f"amqp://{settings.RABBITMQ_USER}:{settings.RABBITMQ_PASS}@{settings.RABBITMQ_HOST}:{settings.RABBITMQ_PORT}//",
    backend=f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/0",
    include=["workers.tasks"]
)

# Optional configurations
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
)

# Optional task routing
celery_app.conf.task_routes = {
    'workers.tasks.*': {'queue': 'default'}
}

# Optional task settings
celery_app.conf.task_annotations = {
    '*': {
        'rate_limit': '10/s'
    }
}

# Make sure this is at the end of the file
if __name__ == '__main__': 
    celery_app.start()

# Import tasks module after Celery app initialization
from workers import tasks  # noqa
