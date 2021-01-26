import json
import uuid

import requests
from celery import Celery

app = Celery('tasks', broker='pyamqp://guest:guest@rabbitmq:5672//')


@app.task
def set_sent_to_true(id: uuid.uuid4):
    url = f'http://127.0.0.1:8000/messages/{id}/'
    data = json.dumps({'sent': True})
    headers = {'Content-Type': 'application/json'}
    requests.put(url, data, headers=headers)
