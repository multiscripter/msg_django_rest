import json

import requests
from celery import Celery

app = Celery('tasks', broker='pyamqp://guest:guest@localhost:5672//')


@app.task
def set_sent_to_true(id):
    url = f'http://127.0.0.1:8000/messages/{id}/'
    data = json.dumps({'sent': True})
    headers = {'Content-Type': 'application/json'}
    requests.put(url, data, headers=headers)
