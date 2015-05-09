import pymysql.cursors
import json


class DB:
    def __init__(self):
        config=''
        with open("db.config") as f:
            config = json.load(f)
        self.con = pymysql.connect(host=config['host'], user=config['user'],
                                   password=config['password'], db=config['db'])
        self.cur = self.con.cursor()
        self.__first = None
        self.__results = None

    def get_results(self):
        if self.__results is None:
            self.__results = self.cur.fetchall()
        return self.__results

    def get_first(self):
        if self.__first is None:
            self.__first = self.cur.fetchone()
        return self.__first

    def action(self, table, action, fields=['*'], where='1',
               where_and=True):  # where can be a string, an array of components or an array of array of components
        """

        :param table: The table to perform the action on
        :param action:
        :param fields: default = ['*']. The list of fields that will be selected
        :param where: default = 1. str,[],(),[[]],(()). Clauses placed in lists or tuples should be in the format (field,operator,value)
        :param where_and: If true will use AND for multiple where clauses if false will use OR
        """
        if type(fields) == list or type(fields)==tuple:
            if (fields):
                for f in fields:
                    if not (f == '*' or f.lower() == 'count(*)' ):
                        if not f.startswith('`'):
                            f = '`' + f
                        if not f.endswith('`'):
                            f = f + '`'
                fields = ','.join(fields)
            else:
                fields = ''
        values = []
        if type(where) == list or type(where) == tuple:  # where is an array
            if type(where[0]) == list or type(where[0]) == tuple:  # where is a 2d array
                statements = []
                for statement in where:
                    values.append(statement[2])
                    statements.append(' '.join(statement[:2]) + '%s')
                if where_and:
                    where = ' AND '.join(statements)
                else:
                    where = ' OR '.join(statements)
            else:
                values.append(where[2])
                where = ' '.join(where[:2]) + '%s'
        sql = '{0} {1} FROM {2} WHERE {3}'.format(action, fields, table, where)
        self.query(sql, values)


    def in_db(self, table, field, value):
        where = [field, '=', value]
        self.action(table, 'SELECT', ['COUNT(*)'], where=where)
        return self.get_first()[0] >= 1

    def id_in_database(self, table, id_val):
        return self.in_db(table, 'id', id_val)

    def insert(self, table, fields):
        keys = fields.keys()
        placeholders = ['%s'] * len(fields)
        values = '(' + ','.join(placeholders) + ')'
        sql = 'INSERT INTO {0} (`{1}`) VALUES {2}'.format(table, '`, `'.join(keys), values)
        self.query(sql, list(fields.values()))

    def query(self, sql, params=()):
        with self.con:
            try:
                self.cur.execute(sql, params)
            except Exception as e:
                # TODO: add proper error reporting
                print('DB-query: ' + str(e))
        self.__first = None
        self.__results = None


    def update(self, table, fields, where=1, where_and=True):
        statement = 'UPDATE {} set'.format(table)
        sets = []
        params = []
        for key, value in fields.items():
            sets.append('`{}` = %s'.format(key))
            params.append(value)
        statement += ','.join(sets)
        statement += " WHERE " + ' '.join(where)
        self.query(statement, params)


    def get(self, table, fields=['*'], where='1',
            where_and=True):
        self.action(table, 'SELECT', fields, where, where_and)
        return self.get_results()

    def get_single(self, table, fields=['*'], where='1',
            where_and=True):
        self.action(table, 'SELECT', fields, where, where_and)
        return self.get_first()