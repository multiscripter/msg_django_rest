import unittest
import uuid
from datetime import datetime
from http import HTTPStatus
from sqlite3 import dbapi2

import requests

from msg_django_rest.settings import PROD_DB_NAME
from msg_django_rest.tests.SQLiteDriver import SQLiteDriver


class TestIntegration(unittest.TestCase):
    """Integration tests."""

    URL = 'http://127.0.0.1:8000/messages/'

    def setUp(self):
        self.data = []
        self.table_name = 'core_message'
        self.driver = SQLiteDriver(dbapi2, {'database': PROD_DB_NAME})
        msg_date = datetime.now().__str__()
        sql1 = 'insert into {} (id, title, text, sent, read, created, updated)'\
            .format(self.table_name)
        for a in range(2):
            self.data.append({
                'id': uuid.uuid4().__str__(),
                'title': f'test-title-{a}',
                'text': f'test text {a}',
                'sent': 0,
                'read': 0,
                'created': msg_date,
                'updated': msg_date
            })
            sql2 = " values ('{}', '{}', '{}', {}, {}, '{}', '{}')".format(
                self.data[a]['id'], self.data[a]['title'], self.data[a]['text'],
                self.data[a]['sent'], self.data[a]['read'], self.data[a]['created'],
                self.data[a]['updated']
            )
            self.driver.insert(sql1 + sql2)

    def tearDown(self):
        self.driver.delete("delete from {} where id in ('{}')".format(
            self.table_name, "', '".join([msg['id'] for msg in self.data])
        ))
        self.driver.con.close()
        self.driver.close()

    def test_get_messages(self):
        """Tests GET request to http://127.0.0.1:8000/messages/"""

        response = requests.get(TestIntegration.URL)
        self.assertEqual(HTTPStatus.OK.value, response.status_code)

        actual = response.json()
        self._process_data()
        for message in self.data:
            self.assertIn(message, actual)

    def _process_data(self) -> None:
        for message in self.data:
            message['sent'] = bool(message['sent'])
            message['read'] = bool(message['read'])
            message['created'] = datetime.strptime(
                message['created'], '%Y-%m-%d %H:%M:%S.%f'
            ).isoformat()
            message['updated'] = datetime.strptime(
                message['updated'], '%Y-%m-%d %H:%M:%S.%f'
            ).isoformat()
