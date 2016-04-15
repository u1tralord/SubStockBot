import market
import command_processor
import threading
from wrappers import db as db_wrapper
from wrappers import reddit
from wrappers.toolbox import*

# Connect to the database
db = db_wrapper.get_instance()

# Load the profile configuration file
config = None
with open("profile.config") as f:
	config = json.load(f)
	f.close()

def handle_posts_thread(post):
	database_entry = db.processed_posts.find_one({"post_id": post.id})
	if database_entry is None and str(post.author) != config['reddit']['username']:
		print("FIXME!!! Somehow the bots outgoing messages are getting added to the db.")
		print("This could quickly fill up the db with useless garbage.")
		print("Only happens when we use the 'send_message' function in reddit.py")
		print("[{}] {}: {}".format("cmt", post.author, post.body))
		db.processed_posts.insert_one({
			'post_id': post.id,
			'utc': current_utc_time()
		})
		command_processor.process_post(post)

# Gets all comments the user was mentioned in, and processes the comment
def respond_to_mentions():
	print("Retrieving Mentions...")
	threads = [threading.Thread(target=handle_posts_thread, args=(post,)) for post in reddit.get_mentions()]
	threads += [threading.Thread(target=handle_posts_thread, args=(post,)) for post in reddit.get_messages()]
	[thread.start() for thread in threads]
	[thread.join() for thread in threads]
	market.match_offers()

# Reads all comments the bot was mentioned in and parses for a command
repeat_task(30, respond_to_mentions)
