from typing import Dict, Any
from msg_django_rest.core.models import Message


def serialize_message(msg: Message) -> Dict[str, Any]:
    return {
        'id': msg.id,
        'title': msg.title,
        'text': msg.text,
        'sent': msg.sent,
        'read': msg.read,
        'created': msg.created.isoformat(),
        'updated': msg.updated.isoformat()
    }
