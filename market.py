from wrappers import db as db_wrapper
from wrappers.toolbox import *
from user import *

'''
    Market interface for all offers, transfers, and trades
    All offers should come through this module

    TODO:
        * Calculate and match offers
        * Actually remove kreddit and stocks for transaction
        * Transfers & Trades
        * Track how much was taken to make sure we give it all back
'''

# Connect to the database
db = db_wrapper.get_instance()

def _place_offer(offer_type, username, stock, quantity, unit_bid):
    db.market.insert_one({
        "offer": offer_type,
        "username": username,
        "stock_name": stock,
        "quantity": quantity,
        "unit_bid": unit_bid,
        "offer_created": current_utc_time()
    })

def place_buy(username, stock, quantity, unit_bid):
    print("{} is buying {} {} stocks at {} kreddit each".format(username, str(quantity), stock, str(unit_bid)))
    user = User(username)
    try:
        user.take_kreddit(float(quantity) * float(unit_bid))
        _place_offer("buy", username, stock, quantity, unit_bid)
    except:
        raise ValueError('Insufficient funds')


def place_sell(username, stock, quantity, unit_bid):
    print("{} is selling {} {} stocks at {} kreddit each".format(username, str(quantity), stock, str(unit_bid)))
    _place_offer("sell", username, stock, quantity, unit_bid)

