from celery import Celery

celery_app = Celery('subscriptions', broker='pyamqp://guest@localhost//')

celery_app.conf.task_routes = {
    'subscriptions.tasks.subscribe': {'queue': 'subscriptions'},
    'subscriptions.tasks.unsubscribe': {'queue': 'subscriptions'},
}