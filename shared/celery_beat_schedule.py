from datetime import timedelta

beat_schedule = {
    'send_collect_news_message_every_hour': {
        'task': 'news_collector.tasks.collect_news',
        'schedule': timedelta(hours=1),
    },
}