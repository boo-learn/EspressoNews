from celery import Celery
from celery.schedules import crontab

broker_url = 'redis://redis:6379/0'
backend_url = 'redis://redis:6379/0'

celery_app = Celery('tasks', broker=broker_url, backend=backend_url)

celery_app.conf.beat_schedule = {
    'hourly-task-collect-news': {
        'task': 'tasks.collect_news',
        'schedule': 3600,  # 3600.0,
        'args': (),
    },
    'daily-task-get-digest': {
        'task': 'tasks.generate_all_digests_for_users',
        'schedule': 120,  # crontab(hour=6, minute=50),
        'args': (),
    },
}
