import sqlite3 as sqlite
import praw
import json
import time
import os
import re
from threading import Timer
from pprint import pprint

#pprint(vars(post))

config = open("profile.config")
config = json.load(config)

r = praw.Reddit("Subreddit stock monitor. More info at /r/subredditstockmarket. "
                "Created by u/u1tralord, u/Obzoen, and u/CubeMaster7  v: 0.0")

# Log into the Reddit API
USERNAME = config["username"]
PASSWORD = config["password"]
r.login(USERNAME, PASSWORD)

# Get subreddit mods for commands that require mod permissions
MODS = r.get_moderators(r.get_subreddit('subredditstockmarket'))

# Path to the database that stores user data and Subreddit metrics
MAIN_DB_FILE = 'db/StockBotData.db'

# Footer added on to the end of all comments
FOOTER = "\n" \
         "---------------------------------------------------------\n" \
         "^(I am just a bot)  \n" \
         "^(Please visit /r/subredditstockmarket for more info!)  \n" \
         "^(If I messed up your request, please reply to this comment)  \n" \
         "^(with /undo withing the next hour)  \n"

# Extracts a list of words separated by spaces following the username mention to the end of the line
def get_command_args(comment):
    # Gets the position of the username mention from the comment
    command_position = comment.body.find("/u/" + USERNAME.lower())
    # Removes a section from the string up to the end of the username mention
    string_after_username_call = comment.body[command_position+len("/u/"+USERNAME):]
    # Removed any text after the end of the current line and splits the remaining text by spacing
    # Ehh, it works. Ugly, but it works
    # \r is necessary for unix (which the bot is running on) and \n for windows
    user_commands = string_after_username_call.strip().strip("\r").strip("\n").split(" ")
    return user_commands

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

'''
This is going to be where most of the processing is done. So far its just a skeleton of the end result, but this is the
basic idea. As long as the function is here, and is in the dictionary "commands", the code should work.

Each of these functions is going to need to accept the args from the user's bot call to for quantity to sell, price to
sell, etc. It also is going to need to accept the instance of a comment to which it will reply (not shown, but it will
just be the comment that mentioned the bot)
'''


def buy(args, comment):
    print("BUY TEST: " + str(args))
    if len(args) >= 4:
            reply_comment(comment, "You just tried to buy {} of {} stock for {}".format(args[1], args[2], args[3]))


def sell(args, comment):
    print("SELL TEST: " + str(args))
    if len(args) >= 4:
        reply_comment(comment, "You just tried to sell {} of {} stock for {}".format(args[1], args[2], args[3]))


def get_stats(args, comment):
    print("STAT TEST: " + str(args))
    if len(args) >= 2:
        reply_comment(comment, "You just tried to get the latest statistics for  {} stocks".format(args[1]))

commands = {
    "buy": buy,
    "sell": sell,
    "info": get_stats
}


# Returns if the arguments are able to be processed as a command
def is_command(command_args):
    return command_args[0].lower() in commands


def respond_to_mentions():
    print("Retrieving Info...")
    for post in r.get_mentions(limit=None):
        # Check to see if the post has already been processed
        if id_in_database(post.id):
            print(post.body)
            store_processed_id(post.id)
            
            command_arguments = get_command_args(post)
            if is_command(command_arguments):
                # Run the command that matches the first argument in the comment. Ex: Buy, sell, etc
                commands[command_arguments[0].lower()](command_arguments, post)


# Check to see if the post has already been processed
def id_in_database(id_val):
    # Create a connection to the main database to store processed post's IDs
    con = sqlite.connect(MAIN_DB_FILE)
    cur = con.cursor()
    cur.execute("SELECT COUNT(*) FROM processed_posts WHERE id='"+id_val+"'")
    id_exists = cur.fetchone()[0] < 1
    con.close()
    return id_exists


# Store the post's ID so it doesnt re-run the post's request
def store_processed_id(id_val):
    con = sqlite.connect(MAIN_DB_FILE)
    cur = con.cursor()
    cur.execute('''INSERT INTO processed_posts(id) VALUES(:id)''', {'id': id_val})
    con.commit()
    con.close()

# Reads all comments the bot was mentioned in and parses for a command
repeat_task(30, respond_to_mentions, ())
