from django.http import HttpResponse
from ratelimit.exceptions import Ratelimited
from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):
    if isinstance(exc, Ratelimited):
        # Write to log.
        return HttpResponse('Sorry you are blocked', status=429)

    # Call REST framework's default exception handler first,
    # to get the standard error response.
    response = exception_handler(exc, context)

    # Now add the HTTP status code to the response.
    if response is not None:
        response.data['status_code'] = response.status_code
    return response
