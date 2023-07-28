import logging

from bot_app.databases.cruds import UserCRUD
from shared.celery_app import celery_app
from shared.db_utils import update_or_create_schedule_in_db

logger = logging.getLogger(__name__)


async def create_mail_rules():
    logger.info("Starting to create mail rules...")
    user_crud = UserCRUD()
    logger.info("Getting settings options for all users...")
    user_ids, users_list_periodicity_options = await user_crud.get_settings_option_for_all_users('periodicity')
    logger.info(f"Got {len(user_ids)} users' settings options.")
    new_schedule = {}
    for user_id, option in zip(user_ids, users_list_periodicity_options):
        try:
            schedule_value = option.value
        except AttributeError:  # если option - это str, и у него нет атрибута value
            schedule_value = '0 */6 */1 */1 */1'
        logger.info(f"Schedule {schedule_value} for {user_id}")
        task_name = f'generate-digest-for-{str(user_id)}'
        task_schedule = {
            'task': 'tasks.generate_digest_for_user',
            'schedule': schedule_value,
            'args': (user_id,),
        }

        new_schedule[task_name] = task_schedule

    logging.info(f"{new_schedule}")
    for task_name, task_info in new_schedule.items():
        logging.info(f"{task_info}")
        await update_or_create_schedule_in_db(task_name, task_info)

    logger.info("Finished creating mail rules.")


async def create_mail_rule(user_id: int):
    logger.info(f"Starting to create mail rule for user {user_id}...")
    user_crud = UserCRUD()
    logger.info(f"Getting settings option for user {user_id}...")
    periodicity_option = await user_crud.get_settings_option_for_user(user_id, 'periodicity')
    logger.info(f"Got settings option for user {user_id}.")

    task_name = f'generate-digest-for-{str(user_id)}'
    task_schedule = {
        'task': 'tasks.generate_digest_for_user',
        'schedule': periodicity_option,
        'args': (user_id, ),
    }
    logging.info(f"{task_schedule}")
    await update_or_create_schedule_in_db(task_name, task_schedule)

    logger.info(f"Finished creating mail rule for user {user_id}.")
