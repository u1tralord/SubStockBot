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
    kreddits = db.get_single('USERS','kreddits',('id','=',str(user_id)))[0]
    if(kreddits>= price):
        sub_reddit_id = db.get_single('SUB_REDDITS', ['id'], ('name', '=', sub_reddit))[0]
        db.update('USERS',{"kreddits":kreddits-price},('id','=',str(user_id)))
        unit_value = round(price / quantity)
        __place_offer(sub_reddit_id, quantity, unit_value, user_id, 'buy')
    else:
        raise ValueError('The user has insufficient funds')



def place_sell(sub_reddit, quantity, price, user_id):
    sub_reddit_id = db.get_single('SUB_REDDITS', ['id'], ('name', '=', sub_reddit))[0]
    quantity_owned = 0
    owned_stocks = db.get('OWNED_STOCKS',['quantity','id'],(('user_id','=',user_id),('sub_reddit_id','=',sub_reddit_id)))
    for row in owned_stocks:
        quantity_owned += row[0]
    if(quantity_owned>=quantity):
        quantity_remaining = quantity
        index =0
        while quantity_remaining>0:
            row_quantity =owned_stocks[index][0]
            if(row_quantity>=quantity_remaining):
                db.update('OWNED_STOCKS',{"quantity":str(row_quantity-quantity_remaining)},('id','=',str(owned_stocks[index][1])))
                quantity_remaining=0
            else:
                db.update('OWNED_STOCKS',{"quantity":str(0)},('id','=',str(owned_stocks[index][1])))
                quantity_remaining-=row_quantity
        unit_value = round(price / quantity)
        __place_offer(sub_reddit_id, quantity, unit_value, user_id, 'sell')
    else:
        raise ValueError('The user has insufficient quantity of stock')


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
                    db.query('UPDATE MARKET SET quantity = quantity-%s WHERE id=%s OR id=%s',(quantity,buy[3],sell[3]))
                    buy_offer = quantity * buy[1]
                    sell_offer = quantity * sell[1]
                    surplus = abs(buy_offer - sell_offer)
                    rate = min((buy[1],sell[1]))
                    if surplus>0:
                        db.query('UPDATE USERS SET kreddits = kreddits+%s WHERE id=%s',(surplus/2,sell[2]))
                        db.query('UPDATE USERS SET kreddits = kreddits+%s WHERE id=%s',(surplus/2,buy[2]))
                    db.insert('OWNED_STOCKS',{"sub_reddit_id":sub_reddit,"user_id":buy[2],"quantity":quantity})
                    db.query('UPDATE USERS SET kreddits = kreddits+%s WHERE id=%s',(quantity*rate,sell[2]))
    db.query('DELETE FROM MARKET WHERE quantity = 0')
