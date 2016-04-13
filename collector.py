import time
import requests
import json
import pprint

from wrappers import db as db_wrapper

db = db_wrapper.get_instance()

def update_stocks():
	for subreddit in db.whitelist.find():
		collectSubStats(sub['subreddit'])

def update_stock_properties(subname):
	db_stock = db.stocks.find_one({'stock_name': subname})
	if(db_stock is None):
		db_stock = {
			"stock_name": subname,
			"bot_value": get_stock_value(subname), # Collector.py should calculate this after collecting necessary data
			"stock_index": 1, # Stock's rank vs other stocks
			"bot_owned_quantity": 10000, # Total stock available for purchase from bot
			"stock_volume": 10000, # Total stock available on market
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

def get_avg_post_score(subname):
	rawPosts = get_json("/r/{}".format(subname))["data"]["children"]
	upvoteTotal = 0
	totalPosts = 0
	for rawPost in rawPosts:
		jsonPostData = rawPost["data"]
		upvoteTotal += jsonPostData["score"]
		totalPosts += 1
	return upvoteTotal/totalPosts

def get_upvote_total(subname):
	rawPosts = get_json("/r/{}".format(subname))["data"]["children"]
	upvoteTotal = 0
	for rawPost in rawPosts:
		jsonPostData = rawPost["data"]
		upvoteTotal += jsonPostData["score"]
	return upvoteTotal

