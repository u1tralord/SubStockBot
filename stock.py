from wrappers import db as db_wrapper

db = db_wrapper.get_instance()



class Stock():
	def __init__(self, stock_name):
		self._stock_name = stock_name
		self._db_stock = None
		self._stock_value = None
		self._stock_volume = None
		self.update()
		
	@property
	def stock_name(self):
		return self._stock_name
		
	@property
	def stock_value(self):
		if self._stock_value == None:
			self.update()
			self._stock_value = self._db_stock['stock_value']
		return self._stock_value
		
	@stock_value.setter
	def stock_value(self, amount):
		if self._db_stock == None or self._stock_value == None:
			self.update()
		self._stock_value = amount
		with dbLock:
			self._db_stock['stock_value'] = amount
		if self._db_stock['stock_value'] < 0:
			self.stock_value = 0
			return #function returns here because of recursion...no need to write to the db twice...
		self.write_db()
		
	@property
	def stock_volume(self):
		self.update()
		if self._stock_volume == None:
			self._stock_volume = self._db_stock['stock_volume']
		return self._stock_volume
		
	@stock_volume.setter
	def stock_volume(self, amount):
		if self._db_stock == None or self._stock_volume == None:
			self.update()
		self._stock_volume = amount
		with dbLock:
			self._db_stock['stock_volume'] = amount
		if self._db_stock['stock_volume'] < 0:
			self.stock_volume = 0
			return #function returns here because of recursion...no need to write to the db twice...
		self.write_db()
		
	def update(self):
		print("FIXME!!! I run twice whenever I should only run once when getting a stocks value!")
		print("Running stock.update()...dummy method")
		'''
		with dbLock:
			db_stock = db.stocks.find_one({'stock_name': self.stock_name})
		'''
		db_stock = None #TEMPORARY!!!
		if db_stock is None:
			db_stock = create_stock(self.stock_name)
		self._db_stock = db_stock
		
	def write_db(self):
		print("Running writ_db...dummy method")
		'''
		with dbLock:
			db.stocks.update_one({'stock_name': self.stock_name}, {
				'$set': self._db_stock
			}, upsert=True)
		'''
		
	def add_value(self, amount):
		self.stock_value += amount
	
	def take_value(self, amount):
		if self.stock_value >= amount:
			self.stock_value -= amount
		else:
			self.stock_value = 0
			
	def add_volume(self, amount):
		self.stock_volume += amount
		
	def take_volume(self, amount):
		if self.stock_volume >= amount:
			self.stock_volume -= amount
		else:
			self.stock_volume = 0
			
def create_stock(stock_name):
	user = {
		"stock_name": stock_name,
		"stock_value": get_initial_stock_value(),
		"stock_volume": get_initial_stock_volume()
	}
	#db.users.insert_one(user)
	return user
	
def get_initial_stock_value():
	return 100
	
def get_initial_stock_volume():
	return 100
	
