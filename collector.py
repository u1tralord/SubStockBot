import time
import requests
import json
import pprint
from wrappers import db as db_wrapper
from wrappers import toolbox
from wrappers import pymo

db = db_wrapper.get_instance()

# Basic Reddit JSON API interface
# Retrieves JSON data from path provided and returns a parsed JSON object
#     path = Reddit path to follow to be prefixed by "http://www.reddit.com/"
#     after (optional) = Integer value for earliest UTC in seconds to retrieve. 
#                        No posts before this limit will be retieved
def get_json(path, after=None):
    url = 'http://www.reddit.com/{}.json?limit=1000'.format(path) #get_json("/r/{}".format(subname)
    if (after):
        url += '&after=' + after
    r = requests.get(url, headers={'user-agent': 'sub_stock_bot/0.0.1'})
    data = r.json()
    return data

def update_stocks():
	whitelist = pymo.find(db.whitelist, {}) #db.whitelist.find()
	for subreddit in whitelist:
		collectSubStats(sub['subreddit'])
		
def update_stock_properties(subname):
	db_stock = pymo.find(db.stocks, {'stock_name': subname}) #db.stocks.find_one({'stock_name': subname})
	if(db_stock is None):
		db_stock = {
			"stock_name": subname,
			"bot_value": get_stock_value(subname), # Collector.py should calculate this after collecting necessary data
			"stock_index": 1, # Stock's rank vs other stocks
			"bot_owned_quantity": 10000, # Total stock available for purchase from bot
			"stock_volume": 10000, # Total stock available on market
			"issued_shares": get_issued_shares(subname)
		}
		db.stocks.insert_one(db_stock)

	##
	# Do stuff here to modify stock properties
	##
	pymo.update_one(db.stocks, {'stock_name': subname}, {'$set': db_stock}, upsert=True) #db.stocks.update_one({'stock_name': subname}, {'$set': db_stock}, upsert=True)
    
#Returns an integer value representing the number of subscribers to a sub.
#	 subname = string value of subreddit to be evaluated
def get_subscribers(rawAboutJson):
	return rawAboutJson['data']['subscribers']

# Returns an integer value representing the calculated stock value
#     subname = string value of subreddit to be evaluated
def get_stock_value(subname):
	rawAboutJson = get_json("/r/{}/about".format(subname))
	rawCommentsJson = get_json("/r/{}/comments".format(subname))
	rawPostsJson = get_json("/r/{}".format(subname))
	rawNewPostsJson = get_json("/r/{}/new".format(subname))

	comment_freq = get_comment_freq(rawCommentsJson)
	post_freq = get_post_freq(rawNewPostsJson)
	upvote_sum = get_upvote_total(rawPostsJson)
	upvote_avg = get_avg_post_score(rawPostsJson)
	subscribers = get_subscribers(rawAboutJson)
	
	# print("{} {} {}".format(comment_freq, upvote_sum, upvote_avg))
	return -1 # Temporary return value

# Returns an integer for the average time between posts.
# Calculating the average difference between the UTC variable on comment json object
#     rawPostsJson = raw json output of get_json() for comments path of desired subreddit
def get_post_freq(rawPostsJson):
	rawPosts = rawPostsJson['data']['children']
	differenceTotal = 0
	for x in range(1, len(rawPosts)):
		diff = abs(rawPosts[x]['data']['created_utc'] - rawPosts[x-1]['data']['created_utc'])
		differenceTotal += diff
	return differenceTotal / (len(rawPosts)-1)

# Returns an integer for the average time between comments.
# Calculating the average difference between the UTC variable on comment json object
#     rawCommentsJson = raw json output of get_json() for comments path of desired subreddit
def get_comment_freq(rawCommentsJson):
	rawComments = rawCommentsJson['data']['children']
	differenceTotal = 0
	for x in range(1, len(rawComments)):
		diff = abs(rawComments[x]['data']['created_utc'] - rawComments[x-1]['data']['created_utc'])
		differenceTotal += diff
	return differenceTotal / (len(rawComments)-1)

# Returns an integer for average post score of all posts provided by the raw json response
#     rawPostsJson = raw json output of get_json() for posts path of desired subreddit
def get_avg_post_score(rawPostsJson):
	upvoteTotal = 0
	totalPosts = 0
	for rawPost in rawPostsJson["data"]["children"]:
		jsonPostData = rawPost["data"]
		upvoteTotal += jsonPostData["score"]
		totalPosts += 1
	return upvoteTotal/totalPosts

# Returns an integer for total post score of all posts provided by the raw json response
#     rawPostsJson = raw json output of get_json() for posts path of desired subreddit
def get_upvote_total(rawPostsJson):
	upvoteTotal = 0
	for rawPost in rawPostsJson["data"]["children"]:
		jsonPostData = rawPost["data"]
		upvoteTotal += jsonPostData["score"]
	return upvoteTotal
	
if __name__ == '__main__':
	#talesfromtechsupport, funny, adviceanimals, askreddit, leagueoflegends, me_irl, crazyideas, accidentalcomedy
	start_time = toolbox.current_utc_time()
	subsTable = ['talesfromtechsupport', 'funny', 'adviceanimals', 'askreddit', 
				'leagueoflegends', 'me_irl', 'crazyideas', 'accidentalcomedy']
	outfile = open('collector_dump.txt', 'w')
	for subname in subsTable:
		get_sub_start_time = toolbox.current_utc_time()
		rawAboutJson = get_json("/r/{}/about".format(subname))
		rawCommentsJson = get_json("/r/{}/comments".format(subname))
		rawPostsJson = get_json("/r/{}".format(subname))
		
		print ('writing {}\'s data to file'.format(subname))
		outfile.write( "-----\n" )
		outfile.write( 'Subname: {}\n'.format(subname) )
		#comment frequency, upvote sum, upvote average, and subscribers
		outfile.write( 'Comment Frequency: {} miliseconds between comments on average.\n'.format(get_comment_freq(rawCommentsJson)) )
		outfile.write( 'Post Frequency: {} miliseconds between posts on average.\n'.format(get_post_freq(rawPostsJson)) )
		outfile.write( 'Upvote Total: {}\n'.format(get_upvote_total(rawPostsJson)) )
		outfile.write( 'Upvote Average: {}\n'.format(get_avg_post_score(rawPostsJson)) )
		outfile.write( 'Subscribers: {}\n'.format(get_subscribers(rawAboutJson)) )
		outfile.write( 'Time to Analyze: {} seconds\n'.format(toolbox.current_utc_time() - get_sub_start_time))
		outfile.write( "-----\n" )
	outfile.write("All subs were analyzed in {} seconds.".format(toolbox.current_utc_time() - start_time))
	outfile.close()
		