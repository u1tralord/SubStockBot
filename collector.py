import time
import requests
import json

from wrappers import db as db_wrapper

db = db_wrapper.get_instance()
'''
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
'''  

#Returns an integer from the average time between comments.
#Calculating the average difference between the UTC variable on comment json object
#reddit.com/r/funny/comments.json
def get_comment_freq(subname):
    # reddit.com/r/funny/comments.json 
    jsonData = get_json('r/' + subname + '/comments')
    #json.encode(data)
    json_to_file('jsontest', jsonData)
    
    #return comment_freq
    
'''
set a difference variable to the difference between the utc of the current comment and the utc of the last comment 
then average all of the differences
'''
    
def json_to_file(filename, jsonData):
    outfile = open(filename + '.json', 'w')
    json.dump(jsonData, outfile, sort_keys = True, indent = 4,
        ensure_ascii=False)
    outfile.close()

def get_json(path, after=None):
    url = 'http://www.reddit.com/{}.json?limit=1000'.format(path)
    if (after):
        url += '&after=' + after
    r = requests.get(url, headers={'user-agent': 'sub_stock_bot/0.0.1'})
    data = r.json()
    return data
    
get_comment_freq('funny')


