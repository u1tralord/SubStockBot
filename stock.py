from wrappers import db as db_wrapper
from wrappers import pymo
from wrappers import toolbox
from threading import Lock
import collector



db = db_wrapper.get_instance()

stockLocks = {}

class Stock():
	def __init__(self, stock_name):
		self._stock_name = stock_name
		self._db_stock = None
		
		if stock_name not in stockLocks:
			stockLocks.update({stock_name: Lock()})
		
		self.update()
		
	@property
	def stock_name(self):
		return self._stock_name
		
	@property
	def stock_value(self):
		with stockLocks[self.stock_name]:
			if self._db_stock == None:
				self.update()
			return self._db_stock['stock_value']
		
	@stock_value.setter
	def stock_value(self, amount):
		with stockLocks[self.stock_name]:
			if self._db_stock == None:
				self.update()
			self._db_stock['last_stock_value_update'] = toolbox.current_utc_time()
			self._db_stock['stock_value'] = amount
			if self._db_stock['stock_value'] < 0:
				self._db_stock['stock_value'] = 0
			self.write_db()
		
	@property
	def last_stock_value_update(self):
		with stockLocks[self.stock_name]:
			if self._db_stock == None:
				self.update()
			return self._db_stock['last_stock_value_update']
		
	@property
	def stock_index(self):
		with stockLocks[self.stock_name]:
			if self._db_stock == None:
				self.update()
			return self._db_stock['stock_index']
		
	@stock_index.setter
	def stock_index(self, amount):
		with stockLocks[self.stock_name]:
			if self._db_stock == None:
				self.update()
			self._db_stock['stock_index'] = amount
			if self._db_stock['stock_index'] < 0:
				self._db_stock['stock_index'] = 0
			self.write_db()
		
	@property
	def stock_volume(self):
		with stockLocks[self.stock_name]:
			if self._db_stock == None:
				self.update()
			return self._db_stock['stock_volume']
		
	@stock_volume.setter
	def stock_volume(self, amount):
		with stockLocks[self.stock_name]:
			if self._db_stock == None:
				self.update()
			self._db_stock['stock_volume'] = amount
			if self._db_stock['stock_volume'] <= 0:
				self._db_stock['stock_volume'] = 0
				self._db_stock['last_volume_reset'] = toolbox.current_utc_time()
			self.write_db()
		
	@property
	def last_volume_reset(self):
		with stockLocks[self.stock_name]:
			if self._db_stock == None:
				self.update()
			return self._db_stock['last_volume_reset']
		
	@property
	def treasury_shares(self):
		with stockLocks[self.stock_name]:
			if self._db_stock == None:
				self.update()
			return self._db_stock['treasury_shares']
		
	@treasury_shares.setter
	def treasury_shares(self, amount):
		with stockLocks[self.stock_name]:
			if self._db_stock == None:
				self.update()
			self._db_stock['treasury_shares'] = amount
			if self._db_stock['treasury_shares'] < 0:
				self._db_stock['treasury_shares'] = 0
			self.write_db()
		
	@property
	def issued_shares(self):
		with stockLocks[self.stock_name]:
			if self._db_stock == None:
				self.update()
			return self._db_stock['issued_shares']
		
	@issued_shares.setter
	def issued_shares(self, amount):
		with stockLocks[self.stock_name]:
			if self._db_stock == None:
				self.update()
			self._db_stock['last_issued_shares_update'] = toolbox.current_utc_time()
			self._db_stock['issued_shares'] = amount
			if self._db_stock['issued_shares'] < 0:
				self._db_stock['issued_shares'] = 0
			self.write_db()
			
	@property
	def last_issued_shares_update(self):
		with stockLocks[self.stock_name]:
			if self._db_stock == None:
				self.update()
			return self._db_stock['last_issued_shares_update']
		
	def update(self):
		print("FIXME!!! I run twice whenever I should only run once when getting a stocks value!")
		print("Running stock.update()...dummy method")
		#self._db_stock = pymo.find_one(db.stocks, {'stock_name': self.stock_name})
		self._db_stock = None #TEMPORARY!!!
		if self._db_stock is None:
			self._init_stock()
		
	def write_db(self):
		print("Running write_db...dummy method")
		#pymo.update_one(db.stocks, {'stock_name': self.stock_name}, {'$set': self._db_stock}, upsert=True)
		
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
			
	def take_shares(self, amount):
		self.treasury_shares += amount
		
	def add_shares(self, amount):
		if self.treasury_shares >= amount:
			self.treasury_shares -= amount
		else:
			self.treasury_shares = 0
			
	def reset_volume(self):
		self.stock_volume = 0

	def update_issued_shares(self):
		rawAboutJson = collector.get_json("/r/{}/about".format(self.stock_name))
		active_traders = collector.get_active_trader_count()
		self.issued_shares = collector.get_subscribers(rawAboutJson)**0.4*active_traders/50
		if self.issued_shares < active_traders/10:
			self.issued_shares = active_traders/10
		
	def update_stock_value(self):
		print ("update_stock_value")
		rawAboutJson = collector.get_json("/r/{}/about".format(self.stock_name))
		rawCommentsJson = collector.get_json("/r/{}/comments".format(self.stock_name))
		rawPostsJson = collector.get_json("/r/{}".format(self.stock_name))
		rawNewPostsJson = collector.get_json("/r/{}/new".format(self.stock_name))

		comment_freq = collector.get_comment_freq(rawCommentsJson)
		post_freq = collector.get_post_freq(rawNewPostsJson)
		upvote_sum = collector.get_upvote_total(rawPostsJson)
		upvote_avg = collector.get_avg_post_score(rawPostsJson)
		subscribers = collector.get_subscribers(rawAboutJson)
		
		self.stock_value = 10/(comment_freq**0.2)+1000/(post_freq**0.5)+upvote_sum/20000+upvote_avg**0.2+subscribers**0.12
		
	def _init_stock(self):
		print ("Initializing Stock")
		
		self._db_stock = {
			"stock_name": self.stock_name,
			"stock_value": -1,
			"last_stock_value_update": -1, #last time the stock's value was updated.
			"stock_index": -1, # Placeholder to be implemented later
			"stock_volume": -1, # Number of stocks traded per day.
			"last_volume_reset": -1, # Keeps track of when the last time the volume was reset.
			"treasury_shares": -1, # Total stock available for purchase from bot
			"issued_shares": -1, #Total number of stocks on the market period
			"last_issued_shares_update": -1 # Keeps track of when the last time the issued_shares was updated.
		}
		
		#db.stocks.insert_one(self._db_stock)
		self.reset_volume()
		self.update_stock_value()
		self.update_issued_shares()
		self.treasury_shares = self.issued_shares
	
if __name__ == '__main__':
	stock = Stock('funny')
	print(" name: {} \n value: {} ~~ last update: {} \n index: {} \n volume: {} ~~ last reset: {} \n treasury: {} \n issued: {} ~~ last update {}".format(
	stock.stock_name,
	stock.stock_value,
	stock.last_stock_value_update,
	stock.stock_index,
	stock.stock_volume,
	stock.last_volume_reset,
	stock.treasury_shares,
	stock.issued_shares,
	stock.last_issued_shares_update
	))
	