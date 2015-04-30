import sqlite3 as sqlite


class DB:
    def __init__(self):
        # Path to the database that stores user data and Subreddit metrics
        MAIN_DB_FILE = 'db/StockBotData.db'
        self.con = sqlite.connect(MAIN_DB_FILE)
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
        for f in fields:
            if not (f == '*' or f.lower() == 'count(*)'):
                if not f.startswith('`'):
                    f = '`' + f
                if not f.endswith('`'):
                    f = f + '`'
        fields = ','.join(fields)

        def fix_string(s):
            def is_number(str1):
                try:
                    float(str1)
                    return True
                except ValueError:
                    return False

            if not is_number(s):
                if not s.startswith("'"):
                    s = "'" + s
                if not s.endswith("'"):
                    s = s + "'"
            return s

        if type(where) == list:  #where is an array
            if type(where[0]) == list:  #where is a 2d array
                for statement in where:
                    statement[2] = fix_string(statement[2])
                    statement = ' '.join(statement)
                if where_and:
                    where = ' AND '.join(where)
                else:
                    where = ' OR '.join(where)
            else:
                where[2] = fix_string(where[2])
            where = ' '.join(where)
        sql = '{0} {1} FROM {2} WHERE {3}'.format(action, fields, table, where)
        print(sql)
        self.cur.execute(sql)
        self.__first = None
        self.__results = None

    def in_db(self, table, field, value):
        where = [field, '=', value]
        self.action(table, 'SELECT', ['COUNT(*)'], where=where)
        return self.get_first()[0] >= 1

    def id_in_database(self, table, id_val):
        return self.in_db(table, 'id', id_val)

    def insert(self, table, fields):
        keys = fields.keys()
        values = '(' + ','.join(['?'] * len(keys)) + ')'
        sql = 'INSERT INTO {0} (`{1}`) VALUES {2}'.format(table, '`, `'.join(keys), values)
        self.cur.execute(sql, list(fields.values()))
        self.con.commit()

