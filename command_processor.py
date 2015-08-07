from wrappers import reddit
import market

'''
    Command Processing Central
    All commands will be added here, and this module will determine which command to run
'''
# Processes the comment and figures out what command to run
def process_post(post):
    command_args = get_command_args(post)
    if is_command(command_args):
        print(post)
        # Run the command that matches the first argument in the comment. Ex: Buy, sell, etc
        commands[command_args[0].lower()](command_args, post)
    else:
        reddit.reply_comment(post, "Command not recognized")

# Extracts a list of words separated by spaces following the username mention to the end of the line
def get_command_args(comment):
    # Gets the position of the username mention from the comment
    command_position = comment.body.find("/u/" + reddit.logged_in_user().lower())
    # Removes a section from the string up to the end of the username mention
    string_after_username_call = comment.body[command_position+len("/u/"+reddit.logged_in_user()):]
    # Removed any text after the end of the current line and splits the remaining text by spacing
    # Ehh, it works. Ugly, but it works
    # \r is necessary for unix (which the bot is running on) and \n for windows
    user_commands = string_after_username_call.strip().strip("\r").strip("\n").split(" ")
    return user_commands

# Comment format: /u/substockbot sell 5 askreddit 50 kreddit
def buy(args, comment):
    if len(args) >= 4:
        print("BUYING : " + str(args))
        username = comment.author.name

        unit_bid = None
        quantity = None
        try:
            unit_bid = float(args[3])
            quantity = float(args[1])
        except ValueError:
            reddit.reply_comment(comment, "Invalid command. Values should not have any symbols or letters")

        if unit_bid is not None and quantity is not None:
            try:
                market.place_buy(username, args[2], quantity, unit_bid)
                reddit.reply_comment(comment, "You just placed an offer to buy for {} of {} stock for {} kreddit each".format(
                    args[1],
                    args[2],
                    args[3]
                ))
            except ValueError as ve:
                reddit.reply_comment(comment, str(ve))

# Comment format: /u/substockbot sell 5 askreddit 50 kreddit
def sell(args, comment):
    if len(args) >= 4:
        print("SELLING : " + str(args))
        username = comment.author.name

        unit_bid = None
        quantity = None
        try:
            unit_bid = float(args[3])
            quantity = float(args[1])
        except ValueError:
            reddit.reply_comment(comment, "Invalid command. Values should not have any symbols or letters")

        if unit_bid is not None and quantity is not None:
            try:
                # market.place_sell(username, stock, quantity, unit_bid)
                reddit.reply_comment(comment, "You just placed an offer to sell for {} of {} stock for {} kreddit each".format(
                    args[1],
                    args[2],
                    args[3]
                ))
            except ValueError as ve:
                reddit.reply_comment(comment, str(ve))

def get_stats(args, comment):
    print("STATs: " + str(args))
    if len(args) >= 2:
        reddit.reply_comment(comment, "You just tried to get the latest statistics for  {} stocks".format(args[1]))

commands = {
    "buy": buy,
    "sell": sell,
    "info": get_stats
}

# Returns if the arguments are able to be processed as a command
def is_command(command_args):
    return command_args[0].lower() in commands