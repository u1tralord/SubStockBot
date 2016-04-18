import praw
import json
import OAuth2Util
from threading import Timer, Lock
from wrappers.toolbox import*

'''
	Reddit wrapper class
'''

# Load the profile configuration file
config = None
with open("profile.config") as f:
	config = json.load(f)
	f.close()
	
oAuthLock = Lock()

with oAuthLock:
	r = praw.Reddit("Subreddit stock monitor. More info at /r/subredditstockmarket."
					"Created by u/u1tralord, u/Obzoen, and u/CubeMaster7  v: 0.0")
				
#Get OAuth2 Token and login.
with oAuthLock:
	o = OAuth2Util.OAuth2Util(r)

# Footer added on to the end of all comments
FOOTER = "\n\n\n" \
		 "---------------------------------------------------------\n" \
		 "^(I am just a bot)  \n" \
		 "^(Please visit /r/subredditstockmarket for more info!)  \n" \
		 "^(If I messed up your request, please reply to this comment)  \n" \
		 "^(with /undo within the next hour)  \n"

logged_in_user = lambda: str(r.user)

def refresh_OAuth(coerce=True):
	with oAuthLock:
		o.refresh(force=coerce)
		
repeat_task(3500, refresh_OAuth)

def get_moderators(subreddit):
	with oAuthLock:
		return r.get_moderators(r.get_subreddit(subreddit))

def is_mod(username, subreddit):
	mod_status = False
	for mod_name in get_moderators(subreddit):
		if str(mod_name) == username:
			mod_status = True
	return mod_status

def get_mentions():
	with oAuthLock:
		return r.get_mentions(limit=None)
	
def get_unread():
	with oAuthLock:
		return r.get_unread(limit=None, unset_has_mail=True)
	
def get_messages():
	with oAuthLock:
		return r.get_messages(limit=None)
		
def get_post_replies():
	with oAuthLock:
		return r.get_post_replies(limit=None)
		
def get_comment_replies():
	with oAuthLock:
		return r.get_comment_replies(limit=None)

# Method for standard commenting by the bot. We should add a footer to the bot with a link to the
# subreddit, and the standard "I AM A BOT" message
def reply_comment(comment, message):
	try:
		with oAuthLock:
			comment.reply(message + FOOTER)
		print(message)
	except praw.errors.RateLimitExceeded as error:
		print('Rate Limit Exceded')
		print('Sleeping for %d seconds' % error.sleep_time)
		Timer(error.sleep_time+1, reply_comment, (comment, message)).start()
		
def send_message(recipient, subject, message):
	try:
		with oAuthLock:
			r.send_message(recipient, subject, message + FOOTER)
		print (message)
	except praw.errors.RateLimitExceeded as error:
		print('Rate Limit Exceded')
		print('Sleeping for %d secconds' % error.sleep_time)
		Timer(error.sleep_time+1, send_message, (recipient, subject, message)).start()
	
# Method for standard commenting by the bot.
def reply(redditThing, message):
	try:
		with oAuthLock:
			redditThing.reply(message + FOOTER)
		print(message)
	except praw.errors.RateLimitExceeded as error:
		print('Rate Limit Exceded')
		print('Sleeping for %d seconds' % error.sleep_time)
		Timer(error.sleep_time, reply, (redditThing, message)).start()

