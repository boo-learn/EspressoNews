from datetime import timedelta

beat_schedule = {
    'send_collect_news_message_every_hour': {
        'task': 'news_collector.tasks.collect_news',
        'schedule': timedelta(hours=1),
    },
    'subscribe_task_every_minute': {
        'task': 'subscriptions.tasks.subscribe',
        'schedule': timedelta(minutes=1),
    },
    'unsubscribe_task_every_minute': {
        'task': 'subscriptions.tasks.unsubscribe',
        'schedule': timedelta(minutes=1),
    },
}