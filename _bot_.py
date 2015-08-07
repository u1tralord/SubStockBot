import market
import command_processor
from wrappers import db as db_wrapper
from wrappers import reddit
from wrappers.toolbox import*

# Connect to the database
db = db_wrapper.get_instance()

# Gets all comments the user was mentioned in, and processes the comment
def respond_to_mentions():
    print("Retrieving Mentions...")
    for post in reddit.get_mentions():
        database_entry = db.processed_posts.find_one({"post_id": post.id})
        if database_entry is None:
            print("New Comment!")
            db.processed_posts.insert_one({
                'post_id': post.id,
                'utc': current_utc_time()
            })
            command_processor.process_post(post)


# Reads all comments the bot was mentioned in and parses for a command
repeat_task(30, respond_to_mentions, ())