import os

from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'WFSR.settings')

app = Celery('WFSR')

app.config_from_object(f'django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()

app.conf.beat_scheduler = 'django_celery_beat.schedulers.DatabaseScheduler'

app.conf.beat_schedule = {
    'collect': {
        'task': 'collector.tasks.collect',
        'schedule': crontab(minute='0', hour='*/1'),
    }
}

app.conf.broker_connection_retry_on_startup = True