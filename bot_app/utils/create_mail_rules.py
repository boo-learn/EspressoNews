import logging

from bot_app.databases.cruds import UserCRUD
from shared.celery_app import celery_app

logger = logging.getLogger(__name__)


async def create_mail_rules():
    user_crud = UserCRUD()
    user_ids, users_list_periodicity_options = await user_crud.get_settings_option_for_all_users('periodicity')
    for user_id, option in zip(user_ids, users_list_periodicity_options):
        task_name = f'generate-digest-for-{str(user_id)}'
        task_schedule = {
            'task': 'tasks.generate_digest_for_user',
            'schedule': option,
            'args': (user_id),
        }

        if task_name not in celery_app.conf.beat_schedule:
            celery_app.conf.beat_schedule[task_name] = task_schedule
            logger.info(f"Task {task_name} has been added")
