import json
from wrappers import db as db_wrapper
from wrappers import reddit

db = db_wrapper.get_instance()

'''
    User database module
    Wrapper class for interfacing user accounts with the mongo database

    Todo:
        * Add/Remove Stock functions
'''

# Load the general settings from file
settings = None
with open("settings.config") as f:
    settings = json.load(f)

class User:
    def __init__(self, username):
        self.username = username
        self.update()

    def update(self):
        db_user = db.users.find_one({'username': self.username})
        if db_user is None:
            db_user = create_user(self.username)
        db_user['permission_level'] = get_permission_level(self.username)
        self.db_user = db_user

    def write_db(self):
        db.users.update_one({'username': self.username}, {
            '$set': self.db_user
        }, upsert=True)

    def add_stock(self, stock_name, quantity):
        self.update()
        stocks = self.db_user['stocks']

        self.db_user['stocks'] = stocks
        self.write_db()

    def take_stock(self, stock_name, quantity):
        self.update()
        # take stock
        self.write_db()

    def add_kreddit(self, amount):
        self.update()
        self.db_user['balance'] = float(self.db_user['balance']) + float(amount)
        self.write_db()

    def take_kreddit(self, amount):
        self.update()
        if float(self.db_user['balance']) > float(amount):
            self.db_user['balance'] = float(self.db_user['balance']) - float(amount)
        else:
            raise ValueError('Insufficient funds')
        self.write_db()

def create_user(username):
    user = {
        "permission_level": get_permission_level(username),
        "username": username,
        "balance": get_initial_balance(),
        "stocks": []
    }
    db.users.insert_one(user)
    return user

def get_initial_balance():
    return 10000

def get_permission_level(username):
    if reddit.is_mod(username, settings['mod_list_sub']):
        return 2
    return 1
