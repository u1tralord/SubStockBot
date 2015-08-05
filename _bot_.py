import praw
import json
from threading import Timer
from pprint import pprint

#pprint(vars(post))
config = None
with open("profile.config") as f:
    config = json.load(f)

r = praw.Reddit("Subreddit stock monitor. More info at /r/subredditstockmarket. "
                "Created by u/u1tralord, u/Obzoen, and u/CubeMaster7  v: 0.0")

# Log into the Reddit API
USERNAME = config["username"]
PASSWORD = config["password"]
r.login(USERNAME, PASSWORD)

# Get subreddit mods for commands that require mod permissions
MODS = r.get_moderators(r.get_subreddit('subredditstockmarket'))

# Footer added on to the end of all comments
FOOTER = "\n" \
         "---------------------------------------------------------\n" \
         "^(I am just a bot)  \n" \
         "^(Please visit /r/subredditstockmarket for more info!)  \n" \
         "^(If I messed up your request, please reply to this comment)  \n" \
         "^(with /undo withing the next hour)  \n"


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
        print("\tRate Limit Exceded")
        print('\tSleeping for %d seconds' % error.sleep_time)
        # time.sleep(error.sleep_time)
        Timer(error.sleep_time, reply_comment, (comment, message + FOOTER)).start()

def respond_to_mentions():
    print("Retrieving Mentions...")
    for post in r.get_mentions(limit=None):
        pprint(vars(post))

# Reads all comments the bot was mentioned in and parses for a command
repeat_task(30, respond_to_mentions, ())