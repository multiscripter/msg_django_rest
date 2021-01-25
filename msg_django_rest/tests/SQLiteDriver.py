from datetime import date, datetime


class SQLiteDriver:
    """MySQL database driver."""

    def __init__(self, adapter, params=None):
        """Initializes instance

        :param params: collection with connection parameters named:
        dbname, host, password, port, user.
        :type params: dictionary
        """

        self.adapter = adapter
        self.con = False
        self.params = params

    def close(self):
        """Closes connection with database.
        """

        if self.con:
            self.con.close()

    def delete(self, query=''):
        """Deletes from database

        :param query: SQL query string.
        :type query: str
        :returns: number of affected rows
        :rtype: int
        """

        return self.execute_sql(query)['affected']

    def execute_sql(self, query=''):
        """Executes SQL query

        :param query: SQL query string.
        :type query: str
        :returns: result dictionary
        :rtype: dict
        """

        cur = None
        query = self.strip_query(query)
        if not self.con:
            self.set_connection()
        result = {}
        try:
            cur = self.con.cursor()
            cur.execute(query)
            self.con.commit()
            if query.lower().startswith('select'):
                result['columns'] = cur.description
                result['rows'] = cur.fetchall()
            result['affected'] = cur.rowcount
        except:
            self.con.rollback()
            if cur:
                cur.close()
            self.close()
            raise

        return result

    def execute_sql_script(self, name):
        """Executes SQL queries from file

        :param name: SQL script name.
        :type name: str
        :returns: number of affected rows
        :rtype: int
        """

        with open(name) as f:
            queries = f.read()
        return self.execute_sql(queries)['affected']

    def insert(self, query=''):
        """Inserts data into database

        :param query: SQL query string.
        :type query: str
        :returns: number of affected rows
        :rtype: int
        """

        return self.execute_sql(query)['affected']

    def is_connected(self):
        """Checks connection openness.

        :returns: True if connection is opened. Otherwise False.
        :rtype: bool
        """

        return self.con and not self.con.is_connected

    def select(self, query=''):
        """Selects data from database.

        :param query: SQL query string.
        :type query: str
        :returns: [{ colName: colVal[, colName: colVal]}[, { . . . }]]
        :rtype: dict list
        """

        fetched = self.execute_sql(query)
        cols = fetched['columns']
        result = []
        for row in fetched['rows']:
            entry = {}
            a = 0
            for val in row:
                if isinstance(val, datetime) or isinstance(val, date):
                    val = val.isoformat()
                entry[cols[a][0]] = val
                a += 1
            result.append(entry)
        return result

    def set_connection(self):
        """Sets connection with database"""

        if self.is_connected():
            return
        if self.params:
            self.con = self.adapter.connect(**self.params)
        else:
            raise Exception('No params for connection')

    def strip_query(self, query=''):
        """Deletes trailing spaces from query string

        :param query: SQL query string.
        :type query: str
        :returns: stripped SQL query string.
        :rtype: str
        """

        query = query.strip()
        if not query:
            raise Exception('Empty query')
        return query

    def update(self, query=''):
        """Updates data in database

        :param query: SQL query string.
        :type query: str
        :returns: number of affected rows
        :rtype: int
        """

        return self.execute_sql(query)['affected']
