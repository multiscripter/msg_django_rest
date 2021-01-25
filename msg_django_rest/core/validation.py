import re
from typing import Any

RULES = [
    '^[a-z0-9]{8}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{12}$'
]

FILTERS = {
    'id': [RULES[0]],
    'title': ['empty']
}


def validate(data: Any, filters: list) -> dict:
    errors = dict()
    for k in filters:
        if k in data:
            if type(data[k]) is str:
                data[k] = data[k].strip()
            for f in FILTERS[k]:
                if f == 'empty':
                    if not data[k]:
                        errors[k] = '{} is empty'.format(k)
                        break
                else:
                    val = data[k]
                    if isinstance(val, object):
                        val = val.__str__()
                    if not re.match(r'{}'.format(f), val):
                        errors[k] = '{} is incorrect'.format(k)
                        break
        else:
            errors[k] = '{} is not set'.format(k)
    return errors
