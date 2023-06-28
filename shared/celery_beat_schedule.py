from datetime import timedelta

beat_schedule = {
    'send_collect_news_message_every_hour': {
        'task': 'news_collector.tasks.collect_news',
        'schedule': timedelta(hours=1),
    },
    'summarize_news_every_minute': {
        'task': 'summary_service.tasks.summarize_news',
        'schedule': timedelta(minutes=1),
    },
}