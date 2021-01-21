import os

from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'msg_django_rest.settings')
# run from project root:
# celery -A msg_django_rest worker -l INFO
app = Celery('msg_django_rest')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
