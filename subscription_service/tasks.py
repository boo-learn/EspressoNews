from shared.celery_app import subscriptions_celery_app

from subscription_service.db_utils import subscribe_to_channel, unsubscribe_from_channel


@subscriptions_celery_app.task
async def subscribe_task(client, channel_username):
    await subscribe_to_channel(client, channel_username)


@subscriptions_celery_app.task
async def unsubscribe_task(client, channel_username):
    await unsubscribe_from_channel(client, channel_username)
