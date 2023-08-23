import logging
import os

from celery import Celery

from shared.db_utils import load_schedule_from_db_sync, update_or_create_schedule_in_db_sync
from shared.loggers import get_logger

logger = get_logger('shared.celery')

broker_url = 'redis://redis:6379/0'
backend_url = 'redis://redis:6379/0'

celery_app = Celery('tasks', broker=broker_url, backend=backend_url)

current_directory = os.getcwd()
schedule_filepath = os.path.join(current_directory, 'schedule.db')

celery_app.conf.update({
    'broker_connection_retry_on_startup': True,
    'beat_scheduler': 'celery.beat.PersistentScheduler',
    'beat_schedule_filename': schedule_filepath
})

# celery_app.conf.beat_schedule = {
#     'every-half-hour-task-collect-news': {
#         'task': 'tasks.collect_news',
#         'schedule': crontab(minute='*/30'),
#         'args': (),
#     },
#     'every-six-hours-task-get-digest': {
#         'task': 'tasks.generate_digest_for_user',
#         'schedule': 120,
#         'args': (95396520,),
#     },
# }

new_schedule = {
}

for task_name, task_info in new_schedule.items():
    update_or_create_schedule_in_db_sync(task_name, task_info)

beat_schedule = load_schedule_from_db_sync()
logger.info(beat_schedule)
celery_app.conf.beat_schedule = beat_schedule
