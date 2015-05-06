__author__ = 'alexthomas'
from wrappers.DB import DB

db = DB()


def __place_offer(sub_reddit_id, quantity, unit_value, user_id, action):
    """

    :param sub_reddit_id:
    :param quantity:
    :param unit_value:
    :param user_id:
    :param action:
    """
    db.insert('MARKET', dict(sub_reddit_id=sub_reddit_id, quantity=quantity, unit_value=unit_value, user_id=user_id,
                             action=action))


def place_buy(sub_reddit, quantity, price, user_id):
    #TODO: check if the user is able to buy
    #TODO: evaluate buy
    sub_reddit_id = db.get_single('SUB_REDDITS', ['id'], ('name', '=', sub_reddit))[0]
    unit_value = round(price / quantity)
    __place_offer(sub_reddit_id, quantity, unit_value, user_id, 'buy')


def place_sell(sub_reddit, quantity, price, user_id):
    #TODO: check if the user is able to sell
    #TODO: evaluate sell
    sub_reddit_id = db.get_single('SUB_REDDITS', ['id'], ('name', '=', sub_reddit))[0]
    unit_value = round(price / quantity)
    __place_offer(sub_reddit_id, quantity, unit_value, user_id, 'sell')


def evaluate_offers():
    for sub_reddit in db.get('SUB_REDDITS', ['id']):
        sub_reddit = sub_reddit[0]
        sells = db.get('MARKET', ['quantity', 'unit_value', 'user_id', 'id'],
                       (('sub_reddit_id', '=', str(sub_reddit)), ('action', '=', 'sell')))
        buys = db.get('MARKET', ['quantity', 'unit_value', 'user_id', 'id'],
                      (('sub_reddit_id', '=', str(sub_reddit)), ('action', '=', 'buy')))
        for sell in sells:
            # filter the buy offers to only the ones that are greater than or equal to the sell price
            possible = [b for b in buys if sell[1] <= b[1]]
            sorted(possible, key=lambda offer: offer[1])  # sort the buy offers buy the price
            if sell[0] > 0:
                for buy in possible:
                    quantity = 0
                    if buy[0] > sell[0]:
                        quantity = sell[0]
                    else:
                        quantity = buy[0]
                    buy_offer = quantity * buy[1]
                    sell_offer = quantity * sell[1]
                    surplus = buy_offer - sell_offer
                    #TODO: distribute surplus
                    #TODO: allocate ownership of stocks
                    #TODO: update Kreddit values
                    #TODO: update stock offers
