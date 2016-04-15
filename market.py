from wrappers import db as db_wrapper
from wrappers.toolbox import *
from user import *
import wrappers.reddit
from threading import Lock
import pymongo

'''
	Market interface for all offers, transfers, and trades
	All offers should come through this module

	TODO:
		* Calculate and match offers
		* Actually remove kreddit and stocks for transaction
		* Transfers & Trades
		* Track how much was taken to make sure we give it all back
'''

# Connect to the database
db = db_wrapper.get_instance()

placeOfferLock = Lock()

def _place_offer(offer_type, username, stock, quantity, unit_bid):
	with placeOfferLock:
        # id = base64.b64encode(uuid.uuid4().bytes)[:5]
		id = 0
		while db.market.find_one({'id': id}):
			id += 1
			
		db.market.insert_one({
			"offer": offer_type,
			"id": id,
			"username": username,
			"stock_name": stock,
			"quantity": quantity,  # Used to keep track of how many stocks are left to buy/sell in this offer
			"total_quantity": quantity,  # This will not be reduced as units of stock from this offer sell.
										 # Used for tracking percentage complete
			"unit_bid": unit_bid,
			"offer_created": current_utc_time_millis()
	})

def place_buy(username, stock, quantity, unit_bid):
	print("{} is buying {} {} stocks at {} kreddit each".format(username, str(quantity), stock, str(unit_bid)))
	user = User(username)
	try:
		user.take_kreddit(float(quantity) * float(unit_bid))
		_place_offer("buy", username, stock, quantity, unit_bid)
	except ValueError as ve:
		raise ve

def place_sell(username, stock, quantity, unit_bid):
	print("{} is selling {} {} stocks at {} kreddit each".format(username, str(quantity), stock, str(unit_bid)))
	user = User(username)
	try:
		user.take_stock(stock, quantity)
		_place_offer("sell", username, stock, quantity, unit_bid)
	except ValueError as ve:
		raise ve

def match_offers():
	print("Matching offers")
	#Orders to buy a stock for x kreddits sorted from lowest to highest
	buys = db.market.find({'offer': 'buy'}).sort("unit_bid", pymongo.ASCENDING)
	for buy in buys:
		for sale in db.market.find({'offer': 'sell', 'stock_name': buy['stock_name']}).sort("unit_bid", pymongo.ASCENDING):
			if float(buy['unit_bid']) >= float(sale['unit_bid']):
				make_transfer(buy, sale)

def delete_offer(offer):
	db.market.delete_one({"_id": offer["_id"]})

def make_transfer(buy, sale):
	buyer = User(buy['username'])
	seller = User(sale['username'])

	transaction_quantity = None

	buy_quantity = float(buy['quantity'])
	sale_quantity = float(sale['quantity'])
	if buy_quantity <= sale_quantity:
		sale['quantity'] = sale_quantity - buy_quantity
		buy['quantity'] = 0
		transaction_quantity = buy_quantity
		db.market.update_one({'_id': sale['_id']}, {
			'$set': sale
		}, upsert=False)
	else:
		buy['quantity'] = buy_quantity - sale_quantity
		sale['quantity'] = 0
		transaction_quantity = sale_quantity
		db.market.update_one({'_id': buy['_id']}, {
			'$set': buy
		}, upsert=False)

	buyer_price = transaction_quantity * float(buy['unit_bid'])
	transaction_price = transaction_quantity * float(sale['unit_bid'])
	buyer_remainder = transaction_price - buyer_price

	# Send private message -> buyer and seller with transaction info
	reddit.send_message(buyer.username, "Stock Bought!", "You have bought {} shares of {} stock from {} for {} kreddits.".format(transaction_quantity, buy['stock_name'], seller.username, transaction_price) )
	reddit.send_message(seller.username, "Stock Sold!", "You have sold {} shares of {} stock to {} for {} kreddits.".format(transaction_quantity, sale['stock_name'], buyer.username, transaction_price) )
	
	if buy['quantity'] == 0:
		delete_offer(buy)
	if sale['quantity'] == 0:
		delete_offer(sale)
	
	seller.add_kreddit(transaction_price)
	buyer.add_kreddit(buyer_remainder)
	buyer.add_stock(sale['stock_name'], transaction_quantity)
	print("Sale {} -> {} for {} of {} stock at {} each (Total: {})".format(seller.username,
																		   buyer.username,
																		   transaction_quantity,
																		   sale['stock_name'],
																		   sale['unit_bid'],
																		   transaction_price))
