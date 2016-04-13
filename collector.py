import time
import requests
import json

from wrappers import db as db_wrapper

db = db_wrapper.get_instance()

def update_stocks():
	for subreddit in db.whitelist.find():
		collectSubStats(sub['subreddit'])

def update_stock_properties(subname):
	db_stock = db.stocks.find_one({'stock_name': subname})
	if(db_stock is None):
		db_stock = {
			"stock_name": subname
			"bot_value": get_stock_value(subname) # Collector.py should calculate this after collecting necessary data
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

def get_stock_value(subname):
	comment_freq = get_comment_freq(subname)
	upvote_sum = get_upvote_total(subname)
	return -1 # Temporary return val 

def get_comment_freq(subname):
	rawData = get_json("/r/{}/comments".format(subname))
	## calculate and return comment frequency
	return -1 # Temporary return value

def get_upvote_total(subname):
	rawData = get_json("/r/{}".format(subname))
	## calculate and return upvote total for posts
	return -1 # Temporary return value


