import praw
import json
from threading import Timer

'''
    Reddit wrapper class
'''

# Load the profile configuration file
config = None
with open("profile.config") as f:
    config = json.load(f)

r = praw.Reddit("Subreddit stock monitor. More info at /r/subredditstockmarket."
                "Created by u/u1tralord, u/Obzoen, and u/CubeMaster7  v: 0.0")

# Log into the Reddit API
r.login(config["reddit"]["username"], config["reddit"]["password"])

# Footer added on to the end of all comments
FOOTER = "\n\n\n" \
         "---------------------------------------------------------\n" \
         "^(I am just a bot)  \n" \
         "^(Please visit /r/subredditstockmarket for more info!)  \n" \
         "^(If I messed up your request, please reply to this comment)  \n" \
         "^(with /undo withing the next hour)  \n"

logged_in_user = lambda: str(r.user)

def get_moderators(subreddit):
    return r.get_moderators(r.get_subreddit(subreddit))

def is_mod(username, subreddit):
    mod_status = False
    for mod_name in get_moderators(subreddit):
        if str(mod_name) == username:
            mod_status = True
    return mod_status

def get_mentions():
    return r.get_mentions(limit=None)

# Method for standard commenting by the bot. We should add a footer to the bot with a link to the
# subreddit, and the standard "I AM A BOT" message
def reply_comment(comment, message):
    try:
        comment.reply(message + FOOTER)
        print(message)
    except praw.errors.RateLimitExceeded as error:
        print('Rate Limit Exceded')
        print('Sleeping for %d seconds' % error.sleep_time)
        Timer(error.sleep_time, reply_comment, (comment, message)).start()