import os
import sys

# No longer need to install dependencies at runtime since we're using a consistent approach
try:
    # Import the celery app from the central module
    from core.celery_app import celery_app
except ImportError as e:
    print(f"Error importing celery_app: {e}")
    # Fall back to using environment variables if import fails
    from celery import Celery
    
    # Create a minimal setup for Celery
    print("Warning: Failed to import settings, using environment variables as fallback")
    
    # Create minimal celery app using environment variables
    celery_app = Celery(
        "webpush_workers",
        broker=f"amqp://{os.environ.get('RABBITMQ_USER', 'guest')}:{os.environ.get('RABBITMQ_PASSWORD', 'guest')}@{os.environ.get('RABBITMQ_HOST', 'localhost')}:5672/",
        backend=f"redis://{os.environ.get('REDIS_HOST', 'localhost')}:{os.environ.get('REDIS_PORT', '6379')}/0"
    )
    
    # Basic configuration
    celery_app.conf.imports = [
        "workers.tasks.notification_tasks",
        "workers.tasks.campaign_tasks"
    ]

# Ensure the celery app is exposed for the worker command
# This ensures the 'workers.celery_worker:celery_app' reference works
if __name__ == "__main__":
    print("Celery worker module loaded successfully")