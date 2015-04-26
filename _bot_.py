import sqlite3 as sqlite
import sys
import praw
import argparse
import json
import os
import re
from pprint import pprint

config = open("profile.config")
config = json.load(config)

r = praw.Reddit("Subreddit stock bot. More info at /r/subredditstockmarket. "
                "Created by u/u1tralord, u/Obzoen, and u/CubeMaster7  v: 0.0")

# Create a connection to the main database to store processed post's IDs
con = sqlite.connect('StockBotData.db')

# Log into the Reddit API
USERNAME = "SubStockBot"
PASSWORD = config["password"]
r.login(USERNAME, PASSWORD)

# Get subreddit mods for verification purposes
MODS = r.get_moderators(r.get_subreddit('subredditstockmarket'))

# Array for storing comments already processed
already_done = []

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


def replyComment(comment, message):
    print(message)

'''
This is going to be where most of the processing is done. So far its just a skeleton of the end result, but this is the
basic idea. As long as the function is here, and is in the dictionary "commands", the code should work.

Each of these functions is going to need to accept the args from the user's bot call to for quantity to sell, price to
sell, etc. It also is going to need to accept the instance of a comment to which it will reply (not shown, but it will
just be the comment that mentioned the bot)
'''


def buy(args, comment):
    print("BUY TEST: " + + str(args))


def sell(args, comment):
    print("SELL TEST: " + str(args))


def test(args, comment):
    print("Secret Test!")
    comment.reply("args" + str(args))

commands = {
    "buy": buy,
    "sell": sell,
    "secretTest": test
}


# Returns if the arguments are able to be processed as a command
def is_command(command_args):
    return command_args[0] in commands

# Reads all comments the bot was mentioned in and parses for a command
with con:
    cur = con.cursor()
    for post in r.get_mentions():
        ##
        ## These next two lines are the broken part. It needs to check if the id exists in the processed_posts table of the db
        ##
        cur.execute("SELECT id FROM processed_posts WHERE id="+post.id)
        if cur.fetchone() is None:
            # pprint(vars(post))
            command_arguments = get_command_args(post)
            if is_command(command_arguments):
                # Run the command that matches the first argument in the comment. Ex: Buy, sell, etc
                commands[command_arguments[0].lower()](command_arguments, post)
            # print(command_arguments)

            # Store the post's ID so it doesnt re-run the post's request
            cur.execute('''INSERT INTO processed_posts(id) VALUES(:id)''', {'id': post.id})
            con.commit()

con.close()
