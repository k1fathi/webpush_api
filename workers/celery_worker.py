import os
import sys

# Add fallback mechanism for settings
def get_settings():
    try:
        from core.config import settings
        return settings
    except Exception as e:
        print(f"Warning: Could not import settings: {e}")
        return None

try:
    # Try to import the celery app with better error handling
    try:
        from core.celery_app import celery_app
    except ImportError as e:
        print(f"Error importing celery_app: {e}")
        # Create celery app directly here as fallback
        from celery import Celery
        
        # Get settings or use environment variables
        settings = get_settings()
        
        if settings:
            # Use settings if available
            broker_url = f"amqp://{settings.RABBITMQ_USER}:{settings.RABBITMQ_PASSWORD}@{settings.RABBITMQ_HOST}:5672/"
            backend_url = f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/0"
        else:
            # Fallback to environment variables
            broker_url = f"amqp://{os.environ.get('RABBITMQ_USER', 'guest')}:{os.environ.get('RABBITMQ_PASSWORD', 'guest')}@{os.environ.get('RABBITMQ_HOST', 'rabbitmq')}:5672/"
            backend_url = f"redis://{os.environ.get('REDIS_HOST', 'redis')}:{os.environ.get('REDIS_PORT', '6379')}/0"
        
        celery_app = Celery(
            "webpush_workers",
            broker=broker_url,
            backend=backend_url
        )
        
        # Minimum configuration
        celery_app.conf.imports = [
            "workers.tasks.notification_tasks",
            "workers.tasks.campaign_tasks"
        ]
        
except Exception as e:
    # Final fallback for any other errors
    print(f"Fatal error: {e}")
    from celery import Celery
    
    # Create minimal app
    celery_app = Celery(
        "webpush_workers",
        broker="amqp://guest:guest@rabbitmq:5672/",
        backend="redis://redis:6379/0"
    )

# Ensure the celery app is exposed for the worker command
# This ensures the 'workers.celery_worker:celery_app' reference works
if __name__ == "__main__":
    print("Celery worker module loaded successfully")