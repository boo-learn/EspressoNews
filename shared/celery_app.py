from celery import Celery

from shared.celery_beat_schedule import beat_schedule
from subscription_service.tasks import subscribe_task, unsubscribe_task


def create_celery_app(name, broker, task_routes, timezone='UTC'):
    app = Celery(name, broker=broker)
    app.conf.task_routes = task_routes
    app.conf.timezone = timezone
    return app


subscriptions_task_routes = {
    'subscription_service.tasks.subscribe_task': {'queue': 'subscriptions', 'rate_limit': '1/m'},
    'subscription_service.tasks.unsubscribe_task': {'queue': 'subscriptions', 'rate_limit': '1/m'},
}

news_collector_task_routes = {
    "news_collector.tasks.collect_news": {"queue": "news_queue"},
}

summarize_task_routes = {
    "summary_service.tasks.summarize_news": {"queue": "summary_queue"},
}

subscriptions_celery_app = create_celery_app('subscriptions', 'redis://redis:6379/0', subscriptions_task_routes)
news_collector_celery_app = create_celery_app('news_collector', 'redis://redis:6379/0',
                                              news_collector_task_routes)
summarize_celery_app = create_celery_app('summary_service', 'redis://redis:6379/0', summarize_task_routes)
news_collector_celery_app.conf.beat_schedule = beat_schedule

