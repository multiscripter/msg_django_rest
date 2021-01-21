import uuid
from datetime import datetime
from django.db import models


# Create your models here.
class Message(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=256)
    text = models.TextField()
    sent = models.BooleanField(default=False)
    read = models.BooleanField(default=False)
    created = models.DateTimeField(default=datetime.now)
    updated = models.DateTimeField(default=datetime.now)
