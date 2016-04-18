import json
from wrappers import db as db_wrapper
from wrappers import reddit
from wrappers.toolbox import *
from wrappers import pymo

db = db_wrapper.get_instance()

'''
	User database module
	Wrapper class for interfacing user accounts with the mongo database

	Todo:
		* Add/Remove Stock functions
'''

whitelist_cache = {
	'subreddits': pymo.find(db.whitelist, {}), #db.whitelist.find()
	'last_updated': current_utc_time()
}

# Load the general settings from file
settings = None
with open("settings.config") as f:
	settings = json.load(f)

class User:
	def __init__(self, username):
		self._username = username
		self._db_user = None
		self.update()
	
	@property
	def username(self):
		return self._username
		
	@property
	def last_active(self):
		if self._db_user == None:
			self.update()
		return self._db_user['last_active']
		
	@last_active.setter
	def last_active(self, amount):
		if self._db_user == None:
			self.update()
		self._db_user['last_active'] = amount
		self.write_db()
	
	@property
	def balance(self):
		if self._db_user == None:
			self.update()
		return self._db_user['balance']
		
	@balance.setter
	def balance(self, amount):
		if self._db_user == None:
			self.update()
		self._db_user['balance'] = amount
		if self._db_user['balance'] < 0:
			self.balance = 0
			return #returns here because of recursion so we aren't writing to the db twice.
		self.write_db()
	
	@property
	def stocks(self):
		if self._db_user == None:
			self.update()
		return self._db_user['stocks']
		
	@stocks.setter
	def stocks(self, list):
		if self._db_user == None:
			self.update()
		self._db_user['stocks'] = list
		self.write_db()
		

	def update(self):
		db_user = pymo.find_one(db.users, {'username': self.username}) #db.users.find_one({'username': self.username})
		if db_user is None:
			db_user = create_user(self.username)
		db_user['permission_level'] = get_permission_level(self.username)
		self._db_user = db_user

	def write_db(self):
		print ('writing to db')
		pymo.update_one(db.users, 
			{'username': self.username}, 
			{ '$set': self._db_user }, 
			upsert=True
			) #db.users.update_one({'username': self.username}, { '$set': self._db_user }, upsert=True)

	def add_stock(self, stock_name, quantity):
		self.update()
		print("Adding {} '{}' stock to user: {} ".format(quantity, stock_name, self.username))
		if is_whitelisted(stock_name):
			stock_found = False
			for stock_entry in self.stocks:
				if stock_entry['stock_name'] == stock_name:
					stock_entry['quantity_owned'] = int(stock_entry['quantity_owned']) + quantity
					stock_found = True
			if not stock_found:
				self.stocks.append({
					'stock_name': stock_name,
					'quantity_owned': quantity
				})
		else:
			raise ValueError('Stock entered is not available for trading')
		print("Finished adding stocks")
		self.write_db()

	def take_stock(self, stock_name, quantity):
		self.update()
		print("Taking {} '{}' stock from user: {} ".format(quantity, stock_name, self.username))
		if is_whitelisted(stock_name):
			has_enough_stock = False
			for stock_entry in self.stocks:
				if stock_entry['stock_name'] == stock_name and int(stock_entry['quantity_owned']) >= quantity:
					stock_entry['quantity_owned'] = int(stock_entry['quantity_owned']) - quantity
					has_enough_stock = True
					#Doesn't work...
					if int(stock_entry['quantity_owned']) == 0:
						stock = pymo.find_one(db.users, {'username': self.username})['stocks']
						with pymo.pymongoLock:
							stock.pop(self.stocks.index(stock_entry))
							self.stocks.pop(self.stocks.index(stock_entry))
						
			if not has_enough_stock:
				raise ValueError('Insufficient quantity of stock')
		else:
			raise ValueError('Stock entered is not available for trading')
		self.write_db()

	def add_kreddit(self, amount):
		print("Adding {} Kreddits to user: {} ".format(amount, self.username))
		self.balance += amount

	def take_kreddit(self, amount):
		print("Removing {} Kreddits from user: {} ".format(amount, self.username))
		if self.balance >= amount:
			self.balance -= amount
		else:
			raise ValueError('Insufficient funds')

def create_user(username):
	user = {
		"permission_level": get_permission_level(username),
		"username": username,
		"last_active": current_utc_time(),
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

def update_whitelist():
	whitelist_cache['subreddits'] = pymo.find(db.whitelist, {}) #db.whitelist.find()

def is_whitelisted(subreddit):
	whitelist = pymo.find(db.whitelist, {}) #db.whitelist.find()
	for sub in whitelist:
		if sub['subreddit'] == subreddit:
			return True
	return False

