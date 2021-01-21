from django.contrib import admin

# Register your models here.
from msg_django_rest.core.models import Message

admin.site.register(Message)
