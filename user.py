import json
from wrappers import db as db_wrapper
from wrappers import reddit
from wrappers.toolbox import *

db = db_wrapper.get_instance()

'''
	User database module
	Wrapper class for interfacing user accounts with the mongo database

	Todo:
		* Add/Remove Stock functions
'''

whitelist_cache = {
	'last_updated': current_utc_time(),
	'subreddits': db.whitelist.find()
}

# Load the general settings from file
settings = None
with open("settings.config") as f:
	settings = json.load(f)

class User:
	def __init__(self, username):
		self._username = username
		self.update()
	
	@property
	def username(self):
		return self._username
		
	@username.setter
	def username(self, strValue):
		try:
			self._username = strValue
		except:
			return False
		return True
	
	@property
	def balance(self):
		return self.db_user['balance']
		
	@balance.setter
	def balance(self, floatValue):
		try:
			self.db_user['balance'] = floatValue
		except:
			return False
		return True
	
	@property
	def stocks(self):
		return self.db_user['stocks']

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
		print("Adding '{}' stock to user: {} ".format(stock_name, self.username))
		if is_whitelisted(stock_name):
			stock_found = False
			for stock_entry in self.db_user['stocks']:
				if stock_entry['stock_name'] == stock_name:
					stock_entry['quantity_owned'] = int(stock_entry['quantity_owned']) + quantity
					stock_found = True
			if not stock_found:
				self.db_user['stocks'].append({
					'stock_name': stock_name,
					'quantity_owned': quantity
				})
		else:
			raise ValueError('Stock entered is not available for trading')
		print("Finished adding stocks")
		self.write_db()

	def take_stock(self, stock_name, quantity):
		print()
		print ("-------------------------------")
		print ("-~+=!|BIG ANNOYING WARNING/REMINDER PRINT!!!|!=+~-")
		print ("FIX ME!!!! >>> I DO NOT DELETE THE DB ENTRY WHEN A STOCK'S QUANTITY == 0!!! >>> I am the take_stock() method in the User class in user.py >>>")
		print ("This could lead to having an unneccessarily large db and will make finding stuff in it slower.")
		print ("-------------------------------")
		print()
		self.update()
		print("Taking '{}' stock from user: {} ", stock_name, self.username)
		if is_whitelisted(stock_name):
			has_enough_stock = False
			for stock_entry in self.db_user['stocks']:
				if stock_entry['stock_name'] == stock_name and int(stock_entry['quantity_owned']) >= quantity:
					stock_entry['quantity_owned'] = int(stock_entry['quantity_owned']) - quantity
					has_enough_stock = True
					'''
					#I don't work...
					if int(stock_entry['quantity_owned']) == quantity:
						self.db_user['stocks'].delete_many({'quantity_owned': 0})
					'''
			if not has_enough_stock:
				raise ValueError('Insufficient quantity of stock')
		else:
			raise ValueError('Stock entered is not available for trading')
		self.write_db()

	def add_kreddit(self, amount):
		self.update()
		self.db_user['balance'] = float(self.db_user['balance']) + float(amount)
		self.write_db()

	def take_kreddit(self, amount):
		self.update()
		if float(self.db_user['balance']) >= float(amount):
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

def update_whitelist():
	whitelist_cache['subreddits'] = db.whitelist.find()

def is_whitelisted(subreddit):
	for sub in db.whitelist.find():
		if sub['subreddit'] == subreddit:
			return True
	return False

