### Simple Message REST service

#### Зависимости:
- Python 3.8.7
- Django==3.1.2
- djangorestframework==3.12.2 
- drf-yasg==1.20.0
- django-ratelimit==3.0.1
- celery==5.0.5
- rabbitmq==3.5.7

### Запуск из корня проекта
#### В Docker контейнере:
- docker-compose build
- docker-compose up -d
#### Сервисы по отдельности:
- python manage.py runserver
- celery -A msg_django_rest worker -l INFO
- sudo -u rabbitmq rabbitmq-server start
### API endpoints:
url: http://127.0.0.1:8000/
- **GET** messages/ - список сообщений
- **GET** messages/\<id>/ - сообщение по id
- **POST** messages/ - создать сообщение
- **PUT** messages/\<id>/ - изменить сообщение
- **DELETE** messages/\<id>/ - удалить сообщение
- **GET** csv/ - список сообщений в формате CSV
- **GET** csv/?limit=1 - ограничить колличество
- **GET** docs/ - документация в формате OpenAPI
- **GET** admin/ - админка. Доступы: admin | admin

#### Пример тела POST и PUT запросов:
```
{
  "title": "test celery",
  "text": "test celery"
}
```
