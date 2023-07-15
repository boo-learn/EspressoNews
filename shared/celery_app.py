from celery import Celery
from celery.schedules import crontab

broker_url = 'redis://redis:6379/0'
backend_url = 'redis://redis:6379/0'

celery_app = Celery('tasks', broker=broker_url, backend=backend_url)

celery_app.conf.update({
    'broker_connection_retry_on_startup': True
})

celery_app.conf.beat_schedule = {
    'every-half-hour-task-collect-news': {
        'task': 'tasks.collect_news',
        'schedule': crontab(minute='*/30'),
        'args': (),
    },
    'every-six-hours-task-get-digest': {
        'task': 'tasks.generate_all_digests_for_users',
        'schedule': crontab(minute='*/2'),
        'args': (),
    },
}
