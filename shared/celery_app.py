from celery import Celery

broker_url = 'redis://redis:6379/0'
backend_url = 'redis://redis:6379/0'

celery_app = Celery('tasks', broker=broker_url, backend=backend_url)
