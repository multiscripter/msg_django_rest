import csv

from django.http import HttpResponse, HttpRequest, JsonResponse
from django.utils.decorators import method_decorator
from ratelimit.decorators import ratelimit
from rest_framework import status
from rest_framework.views import APIView

from msg_django_rest.celery_tasks import set_sent_to_true
from msg_django_rest.core.models import Message
from msg_django_rest.core.serializers import serialize_message
from msg_django_rest.core.validation import validate


class MessageView(APIView):
    """View for handling requests to /message/"""

    def get(self, request: HttpRequest, id: str = None) -> JsonResponse:
        """
        :param request: HttpRequest object.
        :param id: message`s UUID.
        :return: HTTP response in JSON format with status.
        """

        http_status = status.HTTP_200_OK
        data = []
        result_set = None
        if id:
            errors = validate({'id': id}, ['id'])
            if errors:
                http_status = status.HTTP_400_BAD_REQUEST
                data = {
                    'status': 'error',
                    'error': errors
                }
            else:
                result_set = [Message.objects.get(id=id)]
        else:
            result_set = Message.objects.all()
        if result_set:
            data = [serialize_message(message) for message in result_set]
        return JsonResponse(data=data, safe=False, status=http_status)

    @method_decorator(ratelimit(key='ip', rate='10/m', method='POST', block=True))
    def post(self, request: HttpRequest) -> JsonResponse:
        """
        :param request: HttpRequest object containing Message data.
        :return: HTTP response in JSON format with newly created Message.
        """

        http_status = status.HTTP_201_CREATED
        errors = validate(request.data, ['title'])
        if errors:
            http_status = status.HTTP_400_BAD_REQUEST
            data = {
                'status': 'error',
                'error': errors
            }
        else:
            message = Message(**request.data)
            message.save()
            set_sent_to_true.delay(message.id)
            data = serialize_message(message)
        return JsonResponse(data=data, status=http_status)

    def put(self, request: HttpRequest, id: str) -> JsonResponse:
        """
        :param request: HttpRequest object containing Message data.
        :param id: message`s UUID.
        :return: HTTP response in JSON format with status.
        """

        http_status = status.HTTP_200_OK
        data = {'status': 'OK'}
        errors = validate({'id': id}, ['id'])
        if errors:
            http_status = status.HTTP_400_BAD_REQUEST
            data = {
                'status': 'error',
                'error': errors
            }
        else:
            if not Message.objects.filter(id=id).update(**request.data):
                http_status = status.HTTP_500_INTERNAL_SERVER_ERROR
                data = {
                    'status': 'error',
                    'error': 'Message not updated'
                }
        return JsonResponse(data=data, status=http_status)

    def delete(self, request: HttpRequest, id: str) -> JsonResponse:
        """
        :param request: HttpRequest object.
        :param id: message`s UUID.
        :return: HTTP response in JSON format with status.
        """

        http_status = status.HTTP_200_OK
        data = {'status': 'OK'}
        errors = validate({'id': id}, ['id'])
        if errors:
            http_status = status.HTTP_400_BAD_REQUEST
            data = {
                'status': 'error',
                'error': errors
            }
        else:
            try:
                result_set = Message.objects.filter(id=id).delete()
                if not result_set[0]:
                    data = {
                        'status': 'No message deleted'
                    }
            except BaseException as ex:
                http_status = status.HTTP_500_INTERNAL_SERVER_ERROR
                data = {
                    'status': 'error',
                    'error': 'Error during deletion message'
                }
        return JsonResponse(data=data, status=http_status)


class CSVExporter(APIView):
    """View for handling requests to /csv/"""

    def get(self, request: HttpRequest) -> HttpResponse:
        """
        :param request: HttpRequest object with possible GET-parameters.
        :return: HTTP response in CSV format with exported data.
        """

        result_set = Message.objects.order_by('created').all()

        if 'limit' in request.GET:
            limit = int(request.GET['limit'])
            result_set = result_set[:limit]

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="messages.csv"'
        writer = csv.writer(response)
        for result in result_set:
            writer.writerow([
                result.id, result.title, result.text, result.sent,
                result.read, result.created
            ])
        return response
