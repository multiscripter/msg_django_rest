import json
from http import HTTPStatus
from django.http import HttpRequest
from django.test import TestCase

from msg_django_rest.core.models import Message
from msg_django_rest.core.serializers import serialize_message
from msg_django_rest.core.views import MessageView

# Запуск тестов из корня проекта с генерацией покрытия кода.
# coverage erase
# coverage run manage.py test
# coverage html


class TestViews(TestCase):

    def setUp(self):
        self.data = [
            {'title': 'test-title-1', 'text': 'test text 1'},
            {'title': 'test-title-2', 'text': 'test text 2'}
        ]
        for a in range(len(self.data)):
            self.data[a] = Message(**self.data[a])
            self.data[a].save()

    def test_get_messages_list(self):
        view = MessageView()

        response = view.get(HttpRequest())
        self.assertEqual(HTTPStatus.OK.value, response.status_code)

        expected = [serialize_message(a) for a in self.data]
        actual = json.loads(response.content.decode('utf8'))
        self.assertEqual(expected, actual)

    def test_get_message_by_id(self):
        view = MessageView()

        response = view.get(HttpRequest(), self.data[0].id)
        self.assertEqual(HTTPStatus.OK.value, response.status_code)

        expected = serialize_message(self.data[0])
        actual = json.loads(response.content.decode('utf8'))[0]
        self.assertEqual(expected, actual)
