import time
import requests
import json

from wrappers import db as db_wrapper

db = db_wrapper.get_instance()

def updateStocks():
	for subreddit in db.whitelist.find():
		collectSubStats(sub['subreddit'])

def updateStockProperties(subname):
	db_stock = db.stocks.find_one({'stock_name': subname})
	if(db_stock is None):
		db_stock = {
			"stock_name": subname
			"bot_value": 0 # Collector.py should calculate this after collecting necessary data
			"stock_index": 1# Stock's rank vs other stocks
			"bot_owned_quantity": 10000 # Total stock available for purchase from bot
			"stock_volume": 10000 # Total stock available on market
		}
		db.stocks.insert_one(db_stock)

	##
	# Do stuff here to modify stock properties
	##

	db.stocks.update_one({'stock_name': subname}, {
        '$set': db_stock
    }, upsert=True)

def get_json(path, after=None):
    url = 'http://www.reddit.com/{}.json?limit=1000'.format(path)
    if (after):
        url += '&after=' + after
    r = requests.get(url, headers={'user-agent': 'sub_stock_bot/0.0.1'})
    data = r.json()
    return data


