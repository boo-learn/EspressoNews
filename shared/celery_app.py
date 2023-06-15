from celery import Celery


def create_celery_app(name, broker, task_routes, timezone='UTC'):
    app = Celery(name, broker=broker)
    app.conf.task_routes = task_routes
    app.conf.timezone = timezone
    return app


subscriptions_task_routes = {
    'subscriptions.tasks.subscribe': {'queue': 'subscriptions'},
    'subscriptions.tasks.unsubscribe': {'queue': 'subscriptions'},
}

news_collector_task_routes = {
    "news_collector.tasks.collect_news": {"queue": "news_queue"},
}

subscriptions_celery_app = create_celery_app('subscriptions', 'redis://redis:6379/0', subscriptions_task_routes)
news_collector_celery_app = create_celery_app('news_collector', 'redis://redis:6379/0',
                                              news_collector_task_routes)
