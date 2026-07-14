from celery import Celery

from app.core.config import settings

"""
Celery application instance for asynchronous task processing.
"""
celery_app = Celery(
    f"{settings.APP_NAME}",
    broker=settings.CELERY_BROKER_URL,
)

celery_app.conf.update(
    task_default_queue="default",
)

import app.celery.tasks.transcript_tasks