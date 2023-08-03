import logging

from shared.db_utils import update_or_create_schedule_in_db

logger = logging.getLogger(__name__)


async def create_mail_rules(user_ids, users_list_periodicity_options):
    logger.info("Starting to create mail rules...")
    logger.info(f"Got {len(user_ids)} users' settings options.")
    new_schedule = {}
    for user_id, option in zip(user_ids, users_list_periodicity_options):
        logger.info(f"Got {option} user options.")
        try:
            schedule_value = option
        except Exception as e:
            logger.error(f"Error while getting schedule value for user {user_id}: {e}")
            schedule_value = '0 */1 */1 */1 */1'
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


async def create_mail_rule(user_id: int, periodicity_option: str):
    logger.info(f"Starting to create mail rule for user {user_id}...")
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
