import json
import uuid
from http import HTTPStatus
from django.http import HttpRequest
from django.test import TestCase

from msg_django_rest.core.models import Message
from msg_django_rest.core.serializers import serialize_message
from msg_django_rest.core.views import CSVExporter
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

    def test_get_message_by_id_error_incorrect_uuid(self):
        view = MessageView()

        response = view.get(HttpRequest(), 'c_43a6f6-cc08-457c-af8c-7ff7f94405e6')
        self.assertEqual(
            HTTPStatus.BAD_REQUEST.value, response.status_code
        )

        expected = {'status': 'error', 'error': {'id': 'id is incorrect'}}
        actual = json.loads(response.content.decode('utf8'))
        self.assertEqual(expected, actual)

    def test_post_messages(self):
        view = MessageView()
        request = HttpRequest()
        request.data = {'title': 'test-title-3', 'text': 'test text 3'}

        response = view.post(request)
        self.assertEqual(HTTPStatus.CREATED.value, response.status_code)

        actual = json.loads(response.content.decode('utf8'))
        self.assertTrue('id' in actual and actual['id'])
        self.assertEqual(request.data['title'], actual['title'])

    def test_post_messages_error_title_no_set(self):
        view = MessageView()
        request = HttpRequest()
        request.data = {'text': 'test text 3'}

        response = view.post(request)
        self.assertEqual(HTTPStatus.BAD_REQUEST.value, response.status_code)

        expected = {'status': 'error', 'error': {'title': 'title is not set'}}
        actual = json.loads(response.content.decode('utf8'))
        self.assertEqual(expected, actual)

    def test_post_messages_error_title_is_empty(self):
        view = MessageView()
        request = HttpRequest()
        request.data = {'title': '', 'text': 'test text 3'}

        response = view.post(request)
        self.assertEqual(HTTPStatus.BAD_REQUEST.value, response.status_code)

        expected = {'status': 'error', 'error': {'title': 'title is empty'}}
        actual = json.loads(response.content.decode('utf8'))
        self.assertEqual(expected, actual)

    def test_put_message_by_id(self):
        view = MessageView()
        request = HttpRequest()
        request.data = self.data[0]
        request.data.title = 'updated-title-1'
        request.data.read = True
        request.data = serialize_message(request.data)

        response = view.put(request, request.data['id'])
        self.assertEqual(HTTPStatus.OK.value, response.status_code)

        expected = {'status': 'OK'}
        actual = json.loads(response.content.decode('utf8'))
        self.assertEqual(expected, actual)

    def test_put_message_by_id_error_incorrect_uuid(self):
        view = MessageView()

        response = view.put(HttpRequest(), 'c_43a6f6-cc08-457c-af8c-7ff7f94405e6')
        self.assertEqual(
            HTTPStatus.BAD_REQUEST.value, response.status_code
        )

        expected = {'status': 'error', 'error': {'id': 'id is incorrect'}}
        actual = json.loads(response.content.decode('utf8'))
        self.assertEqual(expected, actual)

    def test_put_message_by_id_error_message_not_updated(self):
        view = MessageView()
        request = HttpRequest()
        request.data = self.data[0]
        request.data.title = 'updated-title-1'
        request.data.read = True
        request.data = {}

        response = view.put(request, self.data[0].id)
        self.assertEqual(
            HTTPStatus.INTERNAL_SERVER_ERROR.value, response.status_code
        )

        expected = {
            'status': 'error',
            'error': 'Message not updated'
        }
        actual = json.loads(response.content.decode('utf8'))
        self.assertEqual(expected, actual)

    def test_delete_message_by_id(self):
        view = MessageView()

        response = view.delete(HttpRequest(), self.data[0].id)
        self.assertEqual(HTTPStatus.OK.value, response.status_code)

        expected = {'status': 'OK'}
        actual = json.loads(response.content.decode('utf8'))
        self.assertEqual(expected, actual)

    def test_delete_message_by_id_error_message_not_deleted(self):
        view = MessageView()

        response = view.delete(HttpRequest(), uuid.uuid4().__str__())
        self.assertEqual(HTTPStatus.OK.value, response.status_code)

        expected = {'status': 'No message deleted'}
        actual = json.loads(response.content.decode('utf8'))
        self.assertEqual(expected, actual)

    def test_delete_message_by_id_error_during_deletion_message(self):
        view = MessageView()

        response = view.delete(HttpRequest(), 'Fake-id')
        self.assertEqual(
            HTTPStatus.BAD_REQUEST.value, response.status_code
        )

        expected = {'status': 'error', 'error': {'id': 'id is incorrect'}}
        actual = json.loads(response.content.decode('utf8'))
        self.assertEqual(expected, actual)

    def test_get_CSV(self):
        view = CSVExporter()

        response = view.get(HttpRequest())
        self.assertEqual(HTTPStatus.OK.value, response.status_code)

        expected = [
            '{},{},{},{},{},{}'.format(
                a.id, a.title, a.text, a.sent, a.read, a.created
            ) for a in self.data
        ]
        actual = response.content.decode('utf8').splitlines()
        self.assertEqual(expected, actual)

    def test_get_CSV_param_limit(self):
        view = CSVExporter()
        request = HttpRequest()
        request.GET['limit'] = 1

        response = view.get(request)
        self.assertEqual(HTTPStatus.OK.value, response.status_code)

        expected = ['{},{},{},{},{},{}'.format(
            self.data[0].id, self.data[0].title, self.data[0].text,
            self.data[0].sent, self.data[0].read,
            self.data[0].created
        )]
        actual = response.content.decode('utf8').splitlines()
        self.assertEqual(expected, actual)
