import praw
import argparse
from pprint import pprint

r = praw.Reddit("Subreddit stock bot. More info at /r/subredditstockmarket. "
                "Created by u/u1tralord, u/Obzoen, and u/CubeMaster7  v: 0.0")

# Reads the password from the command line so it isn't here in plaintext
parser = argparse.ArgumentParser(description='Start the StockBot')
parser.add_argument('password', type=str, help='password')
args = parser.parse_args()

# Log into the Reddit API
USERNAME = "SubStockBot"
PASSWORD = args.password;
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
    user_commands = string_after_username_call[:-len(string_after_username_call)+string_after_username_call.find("\n")].strip().split(" ")
    return user_commands


'''
This is going to be where most of the processing is done. So far its just a skeleton of the end result, but this is the
basic idea. As long as the function is here, and is in the dictionary "commands", the code should work.

Each of these functions is going to need to accept the args from the user's bot call to for quantity to sell, price to
sell, etc. It also is going to need to accept the instance of a comment to which it will reply (not shown, but it will
just be the comment that mentioned the bot)
'''


def buy(args):
    print("BUY TEST: " + args)


def sell(args):
    print("BUY TEST: " + args)

commands = {
    "buy": buy,
    "sell": sell
}


# Returns if the arguments are able to be processed as a command
def is_command(command_args):
    return command_args[0] in commands

# Reads all comments the bot was mentioned in and parses for a command
for post in r.get_mentions():
    command_arguments = get_command_args(post)
    if is_command(command_arguments):
        commands[command_arguments[0]]()
        print(command_arguments)
    #pprint(vars(comment))