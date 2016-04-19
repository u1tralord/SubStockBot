print("Starting...")
from wrappers.toolbox import*
print("Imported Toolbox...")
startUTC = current_utc_time()
from wrappers import reddit
print("{} seconds to connect to reddit.".format(current_utc_time() - startUTC))
nextUTC = current_utc_time()
import command_processor
print("{} seconds to import command_processor.".format(current_utc_time() - nextUTC))
nextUTC = current_utc_time()
from wrappers import db as db_wrapper
import market
import threading
from wrappers import pymo
import time
print("{} seconds to import the rest of the libraries.".format(current_utc_time() - nextUTC))

db = db_wrapper.get_instance()

# Connect to the database
db = db_wrapper.get_instance()

# Load the profile configuration file
config = None
with open("profile.config") as f:
	config = json.load(f)
	f.close()

def handle_posts_thread(post):
	database_entry = pymo.find_one(db.processed_posts, {"post_id": post.id})  #db.processed_posts.find_one({"post_id": post.id})
	if database_entry is None and str(post.author) != config['reddit']['username']:
		print("[{}] {}: {}".format("cmt", post.author, post.body))
		db.processed_posts.insert_one({
			'post_id': post.id,
			'utc': current_utc_time()
		})
		command_processor.process_post(post)
		
# Gets all comments the user was mentioned in, and processes the comment
def respond_to_mentions():
	while True:
		startUTC = current_utc_time()
		max_threads = 50
		print("Retrieving Posts...")
		
		#For multi-threading
		threads = [threading.Thread(target=handle_posts_thread, args=(post,)) for post in reddit.get_mentions()]
		threads += [threading.Thread(target=handle_posts_thread, args=(post,)) for post in reddit.get_messages()]
		threads += [threading.Thread(target=handle_posts_thread, args=(post,)) for post in reddit.get_comment_replies()]
		
		''' #For sequential processing
		posts = [post for post in reddit.get_mentions()]
		posts += [post for post in reddit.get_messages()]
		posts += [post for post in reddit.get_comment_replies()]
		'''
		
		startThreadsUTC = current_utc_time()
		active_threads = []
		print("+Starting Threads+")
		''' #For sequential processing
		for post in posts:
			handle_posts_thread(post)
		print("It took {} seconds to process all tasks sequentially".format(current_utc_time() - startThreadsUTC))
		'''
		
		#For multi-threading
		while threads:
			if threading.active_count() < max_threads:
				current_thread = threads.pop(0)
				active_threads.append(current_thread)
				current_thread.start()
		[thread.join() for thread in active_threads]
		
		print("--")
		print("It took {} seconds to process all threads {} threads at a time.".format(current_utc_time() - startThreadsUTC, max_threads))
		print("--")
		
		market.match_offers()
		while current_utc_time() - startUTC < 30:
			time.sleep(0.1)

# Reads all comments the bot was mentioned in and parses for a command
print("I took {} seconds to start up in total.".format(current_utc_time() - startUTC))
#repeat_task(30, respond_to_mentions)
respond_to_mentions()
