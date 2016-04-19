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
import time
print("{} seconds to import the rest of the libraries.".format(current_utc_time() - nextUTC))

# Connect to the database
db = db_wrapper.get_instance()

# Load the profile configuration file
config = None
with open("profile.config") as f:
	config = json.load(f)
	f.close()

def handle_posts(post):
	database_entry = db.processed_posts.find_one({"post_id": post.id})
	if database_entry is None and str(post.author) != config['reddit']['username']:
		print("[{}] {}: {}".format("cmt", post.author, post.body))
		db.processed_posts.insert_one({
			'post_id': post.id,
			'utc': current_utc_time()
		})
		command_processor.process_post(post)
		
# Starts the main_loop.
def main_loop():
	while True:
		startUTC = current_utc_time()
		
		print("+Retrieving Posts+\n")
		posts = [post for post in reddit.get_mentions()]
		posts += [post for post in reddit.get_messages()]
		posts += [post for post in reddit.get_comment_replies()]
		print("\nIt took {} seconds to retrieve posts.\n".format(current_utc_time() - startUTC))
		
		starthandleUTC = current_utc_time()
		print("+Handling Posts+")
		[handle_posts(post) for post in posts]
		print("\nIt took {} seconds to handle all posts\n".format(current_utc_time() - starthandleUTC))
		
		print("\nIt took {} seconds to retrieve and handle all posts in total\n".format(current_utc_time() - startUTC))
		
		market.match_offers()
		
		print("\nIt took {} seconds in total to fully process all tasks\n".format(current_utc_time() - startUTC))
		
		while current_utc_time() - startUTC < 30:
			time.sleep(0.1)

if __name__ == '__main__':
	print("{} seconds to start up in total.\n".format(current_utc_time() - startUTC))
	main_loop()
