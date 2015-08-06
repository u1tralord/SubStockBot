import praw
import json
import pymongo
from threading import Timer
from pprint import pprint
import time

# Load the profile configuration file
config = None
with open("profile.config") as f:
    config = json.load(f)

# Connect to the database
connection=pymongo.MongoClient(config["database"]["host"], int(config["database"]["port"]))
db = connection[config["database"]["db_name"]]
db.authenticate(config["database"]["username"], config["database"]["password"])


r = praw.Reddit("Subreddit stock monitor. More info at /r/subredditstockmarket. "
                "Created by u/u1tralord, u/Obzoen, and u/CubeMaster7  v: 0.0")

# Log into the Reddit API
r.login(config["reddit"]["username"], config["reddit"]["password"])

# Get subreddit mods for commands that require mod permissions
MODS = r.get_moderators(r.get_subreddit('subredditstockmarket'))

# Footer added on to the end of all comments
FOOTER = "\n" \
         "---------------------------------------------------------\n" \
         "^(I am just a bot)  \n" \
         "^(Please visit /r/subredditstockmarket for more info!)  \n" \
         "^(If I messed up your request, please reply to this comment)  \n" \
         "^(with /undo withing the next hour)  \n"


current_utc_time = lambda: int(round(time.time()))

# Runs a task at a specified interval.
#     delay = time in seconds between runs
#     action = function name to be repeated
#     actionargs = args to be passed to action function
def repeat_task(delay, action, actionargs=()):
    Timer(delay, repeat_task, (delay, action, actionargs)).start()
    action(*actionargs)
    
# Method for standard commenting by the bot. We should add a footer to the bot with a link to the
# subreddit, and the standard "I AM A BOT" message
def reply_comment(comment, message):
    try:
        print(message)
        comment.reply(message + FOOTER)
    except praw.errors.RateLimitExceeded as error:
        print('Rate Limit Exceded')
        print('Sleeping for %d seconds' % error.sleep_time)
        # time.sleep(error.sleep_time)
        Timer(error.sleep_time, reply_comment, (comment, message + FOOTER)).start()

# Processes the comment and figures out what command to run
def process_post(post):
    print(post)
    # reply_comment(post, "Reply Bot")

# Gets all comments the user was mentioned in, and processes the comment
def respond_to_mentions():
    print("Retrieving Mentions...")
    for post in r.get_mentions(limit=None):
        database_entry = db.processed_posts.find_one({"post_id": post.id})
        if database_entry is None:
            print("New Comment!")
            db.processed_posts.insert_one({
                'post_id':post.id,
                'utc':current_utc_time()
            })
            process_post(post)


# Reads all comments the bot was mentioned in and parses for a command
repeat_task(30, respond_to_mentions, ())