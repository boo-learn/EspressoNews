import asyncio
import logging

from shared.config import RABBIT_HOST
from shared.rabbitmq import Subscriber, QueuesType
from subscription_service.db_utils import add_subscription, is_have_subscription, \
    get_random_account_exclude_most_subscribed
from tasks import subscribe_task, unsubscribe_task, send_to_subscribe_channel

# Configuring logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

logger = logging.getLogger(__name__)


async def handle_subscription(message: str):
    channel_username = message
    try:
        logging.info(f"Channel username: {channel_username}")
        is_subscribed = await is_have_subscription(channel_username)
        if not is_subscribed:
            account = await get_random_account_exclude_most_subscribed()
            logging.info(f"Account with least subscriptions: {account.phone_number}")
            await add_subscription(account.account_id, channel_username)
            subscribe_task.apply_async(args=[account.account_id, channel_username])
        else:
            logging.info(f"Channel {channel_username} already subscribed")
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        await send_to_subscribe_channel("subscribe", channel_username)


async def handle_unsubscription(message: str):
    logging.info(f"Message: {message}")
    channel_username = message[0]
    account_id = message[1]
    logging.info(f"Unsubscribing from channel {channel_username} with account {account_id}")
    unsubscribe_task.apply_async(args=[account_id, channel_username])


async def main():
    logger.info("Starting main function...")
    subscriber = Subscriber(host=RABBIT_HOST, queue=QueuesType.subscription_service)
    subscriber.subscribe("subscribe", handle_subscription)
    subscriber.subscribe("unsubscribe", handle_unsubscription)
    logger.info("Main function has been started...")
    await subscriber.run()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    try:
        loop.create_task(main())
        loop.run_forever()
    finally:
        logger.info("Closing the event loop...")
        loop.close()
