import asyncio

from shared.config import RABBIT_HOST
from shared.loggers import get_logger
from shared.rabbitmq import Subscriber, QueuesType
from subscription_service.db_utils import add_subscription, is_have_subscription, get_account_with_least_subscriptions
from tasks import subscribe_task, unsubscribe_task, send_to_subscribe_channel

# Configuring logging
logger = get_logger('subscription.main')


async def handle_subscription(message: str):
    channel_username = message
    local_logger = logger.bind(channel=channel_username)
    try:
        local_logger.info('Subscribing to channel')
        is_subscribed = await is_have_subscription(channel_username)
        if not is_subscribed:
            account = await get_account_with_least_subscriptions()
            local_logger.info('Account chosen', phone_number=account.phone_number)
            await add_subscription(account.account_id, channel_username)
            subscribe_task.apply_async(args=[account.account_id, channel_username])
        else:
            local_logger.warn("Channel already subscribed")
    except Exception as e:
        local_logger.exception("Error subscription to channel", error=e)


async def handle_unsubscription(message: str):
    channel_username = message[0]
    account_id = message[1]
    logger.info("Unsubscribing from channel", channel=channel_username, account=account_id)
    unsubscribe_task.apply_async(args=[account_id, channel_username])


async def main():
    logger.info("Starting main function")
    subscriber = Subscriber(host=RABBIT_HOST, queue=QueuesType.subscription_service)
    subscriber.subscribe("subscribe", handle_subscription)
    subscriber.subscribe("unsubscribe", handle_unsubscription)
    logger.info("Main function has been started")
    await subscriber.run()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    try:
        loop.create_task(main())
        loop.run_forever()
    finally:
        logger.info("Closing the event loop")
        loop.close()
