from wrappers import reddit
import market
from stock import *
from user import *
import pymongo

'''
	Command Processing Central
	All commands will be added here, and this module will determine which command to run
'''

db = db_wrapper.get_instance()

# Processes the comment and figures out what command to run
def process_post(post):
	command_args = str(post.body).split(" ")
	if '/u/' in command_args[0]:
		command_args.pop(0)
		
	print ("Body - " +str(post.body))
	print ("Args - " +str(command_args))
		
	if is_command(command_args):
		print(post)
		# Run the command that matches the first argument in the comment. Ex: Buy, sell, etc
		commands[command_args[0].lower()](command_args, post)
	else:
		print('Command not recognized ' + command_args[0].lower())
		print(str(commands))
		reddit.reply(post, "Command not recognized")

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
			reddit.reply(comment, "Invalid command. Values should not have any symbols or letters")

		if unit_bid is not None and quantity is not None:
			try:
				market.place_buy(username, args[2], quantity, unit_bid)
				reddit.reply(comment, "You just placed an offer to buy for {} of {} stock for {} kreddit each".format(
					args[1],
					args[2],
					args[3]
				))
			except ValueError as ve:
				reddit.reply(comment, str(ve))

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
			reddit.reply(comment, "Invalid command. Values should not have any symbols or letters")

		if unit_bid is not None and quantity is not None:
			try:
				market.place_sell(username, args[2], quantity, unit_bid)
				reddit.reply(comment, "You just placed an offer to sell for {} of {} stock for {} kreddit each".format(
					args[1],
					args[2],
					args[3]
				))
			except ValueError as ve:
				reddit.reply(comment, "You just placed an offer to sell for {} of {} stock for {} kreddit each".format(
					args[1],
					args[2],
					args[3]
				))
			except ValueError as ve:
				reddit.reply(comment, str(ve))

def get_stats(args, comment):
	print("STATs: " + str(args))
	if len(args) >= 2:
		reddit.reply(comment, "You just tried to get the latest statistics for  {} stocks".format(args[1]))

def get_profile(args, comment):
	print("Commenting Profile")
	username = comment.author.name
	user = User(username)
	stocks = user.stocks
	balance = user.balance
	table = "Stock Name|Stock Quantity|Stock Value\n" \
			":--|--:|--:\n"
	for stock in stocks:
		stockObj = Stock(stock['stock_name'])
		table += "{}|{}|{}\n".format(stockObj.stock_name, stock['quantity_owned'], stockObj.stock_value)

	profile_comment = "{}\'s Profile:  \nBalance: {}  \n\n\n".format(username, balance) + table
	reddit.reply(comment, profile_comment)

def get_orders(args, comment):
	print("Commenting Orders")
	username = comment.author.name
	buys = db.market.find({'offer': 'buy', 'username': username}).sort("offer_created", 1)
	sells = db.market.find({'offer': 'sell', 'username': username}).sort("offer_created", 1)
	buyTable = "~+=|You Want to Buy|=+~\n\n\n"
	buyTable += "Stock Name|Asking Bid|Quantity|Order Id\n" \
			   ":--|:--|--:|--:\n"
	for buyoffer in buys:
		buyTable += "{}|{}|{}/{}|{}\n".format(buyoffer['stock_name'], buyoffer['unit_bid'], buyoffer['quantity'], buyoffer['total_quantity'], buyoffer['id'])
	buyTable += '\n\n\n'
	sellTable = "~+=|You Want to Sell|=+~\n\n\n"
	sellTable += "Stock Name|Asking Price|Quantity|Order Id\n" \
				":--|:--|--:|--:\n"
	for selloffer in sells:
		sellTable += "{}|{}|{}/{}|{}\n".format(selloffer['stock_name'], selloffer['unit_bid'], selloffer['quantity'], selloffer['total_quantity'], selloffer['id'])
		
	orders_comment = "{}\'s Orders:  \n\n\n".format(username) + buyTable + sellTable
	reddit.reply(comment, orders_comment)
	
def cancel_order(args, comment):
	if len(args) >= 2:
		print ("Canceling: " + str(args))
		username = comment.author.name
		user = User(username)

		orderId = None
		try:
			orderId = int(args[1])
		except ValueError:
			reddit.reply(comment, "Invalid command. Values should not have any symbols or letters")
		
		if orderId is not None:
			try:
				order = db.market.find_one({'id': orderId, 'username': username})
				print(str(order['offer']))
				if order['offer'] == 'sell':
					reddit.reply(comment, "Canceled {} order Id: {} for {} kreddits. You have reclaimed {} shares of {} stock.".format(order['offer'], order['id'], order['unit_bid'], order['quantity'], order['stock_name']))
					user.add_stock(order['stock_name'], order['quantity'])
				elif order['offer'] == 'buy':
					reddit.reply(comment, "Canceled {} order Id: {} for {} shares of {} stock. You have reclaimed {} kreddits".format(order['offer'], order['id'], order['quantity'], order['stock_name'], order['unit_bid']*order['quantity']))
					user.add_kreddit(order['unit_bid']*order['quantity'])
				market.delete_offer(order)
				
			except ValueError:
				reddit.reply(comment, "Invalid command. Does this order belong to you?")
		
def list_all_orders(args, comment):
	if len(args) >= 2:
		print("Commenting Market List")
		username = comment.author.name
		
		sells = db.market.find({'offer': 'sell', 'stock_name': args[1]}).sort("unit_bid", pymongo.ASCENDING)
		buys = db.market.find({'offer': 'buy', 'stock_name': args[1]}).sort("unit_bid", pymongo.DESCENDING)
		
		sellTable = "~+=|People Want to Sell|=+~\n\n\n"
		sellTable += "Seller|Asking Price|Quantity|Order Id\n" \
					":--|:--|--:|--:\n"
		for selloffer in sells:
			sellTable += "{}|{}|{}/{}|{}\n".format(selloffer['username'], selloffer['unit_bid'], selloffer['quantity'], selloffer['total_quantity'], selloffer['id'])
		sellTable += "\n\n\n"
		
		buyTable = "~+=|People Want to Buy|=+~\n\n\n"
		buyTable += "Buyer|Asking Bid|Quantity|Order Id\n" \
				   ":--|:--|--:|--:\n"
		for buyoffer in buys:
			buyTable += "{}|{}|{}/{}|{}\n".format(buyoffer['username'], buyoffer['unit_bid'], buyoffer['quantity'], buyoffer['total_quantity'], buyoffer['id'])
			
		orders_comment = "Market List:  \n\n\n" + sellTable + buyTable
		reddit.reply(comment, orders_comment)

commands = {
	"buy": buy,
	"sell": sell,
	"info": get_stats,
	"profile": get_profile,
	"orders": get_orders,
	"cancel": cancel_order,
	"market": list_all_orders
}

# Returns if the arguments are able to be processed as a command
def is_command(command_args):
	return command_args[0].lower() in commands
	