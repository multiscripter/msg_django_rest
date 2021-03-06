# Generated by Django 3.1.2 on 2021-01-21 10:31

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.UUIDField(primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=256)),
                ('text', models.TextField()),
                ('sent', models.BooleanField(default=False)),
                ('read', models.BooleanField(default=False)),
                ('created', models.DateTimeField(default=datetime.datetime.now)),
                ('updated', models.DateTimeField(default=datetime.datetime.now)),
            ],
        ),
    ]
