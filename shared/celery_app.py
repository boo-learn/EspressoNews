from celery import Celery
from celery.schedules import crontab

broker_url = 'redis://redis:6379/0'
backend_url = 'redis://redis:6379/0'

celery_app = Celery('tasks', broker=broker_url, backend=backend_url)

celery_app.conf.beat_schedule = {
    'run-every-2-minutes': {
        'task': 'tasks.collect_news',
        'schedule': 30,  # 3600.0,
        'args': (),
    },
}
