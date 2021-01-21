import csv

from django.http import HttpResponse
from django.utils.decorators import method_decorator
from ratelimit.decorators import ratelimit
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from msg_django_rest.celery_tasks import set_sent_to_true
from msg_django_rest.core.models import Message
from msg_django_rest.core.serializers import serialize_message


class MessageView(APIView):
    def get(self, request, id=None):
        if id:
            result_set = [Message.objects.get(id=id)]
        else:
            result_set = Message.objects.all()
        data = [serialize_message(item) for item in result_set]
        return Response(data=data)

    @method_decorator(ratelimit(key='ip', rate='1/m', method='POST', block=True))
    def post(self, request):
        http_status = status.HTTP_201_CREATED
        message = Message(**request.data)
        message.save()
        set_sent_to_true.delay(message.id)
        data = serialize_message(message)
        return Response(data=data, status=http_status)

    def put(self, request, id):
        http_status = status.HTTP_200_OK
        data = {'status': 'ok'}
        if not Message.objects.filter(id=id).update(**request.data):
            http_status = status.HTTP_500_INTERNAL_SERVER_ERROR
            data = {
                'status': 'error',
                'error': 'Message not updated'
            }
        return Response(data=data, status=http_status)

    def delete(self, request, id):
        http_status = status.HTTP_200_OK
        data = {'status': 'ok'}
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
        return Response(data=data, status=http_status)


class CSVExporter(APIView):
    def get(self, request):
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
