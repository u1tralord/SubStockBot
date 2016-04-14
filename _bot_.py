import market
import command_processor
import threading
from wrappers import db as db_wrapper
from wrappers import reddit
from wrappers.toolbox import*

# Connect to the database
db = db_wrapper.get_instance()

def handle_posts_thread(post):
	database_entry = db.processed_posts.find_one({"post_id": post.id})
	if database_entry is None:
		print("New Comment!")
		print(post)
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
