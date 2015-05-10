__author__ = 'alexthomas'

import time
import json
import requests
from wrappers.DB import get_instance


def __get_json(path, after=None):
    url = 'http://www.reddit.com/{}.json?limit=100'.format(path)
    if after:
        url += '&after=' + after
    r = requests.get(url, headers={'user-agent': 'sub_stock_bot/0.0.1'})
    data = r.json()
    return data


def __get_all(path, start_time, end_time):
    results = []
    run = True
    after = None
    while run:
        try:
            data = __get_json(path, after)['data']
            after = data['after']
            for child in data['children']:
                child = child['data']
                if start_time < child['created_utc'] < end_time:
                    results.append(child)
                elif child['created_utc'] < end_time:
                    run = False
        except Exception as e:
            print(e)
        if not after:
            run = False
    return results


def __get_posts(sub_reddit, now, start_time):
    """

    :param sub_reddit:
    :param now:
    :param start_time: The time of the earliest post
    :return:
    """
    end_time = now
    path = 'r/{}/new'.format(sub_reddit)
    return __get_all(path, start_time, end_time)


def __get_comments(sub_reddit, now, start_time):
    """

    :param sub_reddit:
    :param now:
    :param start_time: The time of the earliest comment
    :return:
    """
    end_time = now
    path = 'r/{}/comments'.format(sub_reddit)
    return __get_all(path, start_time, end_time)


def collect():
    beginning = time.time()
    db = get_instance('collector')
    db.query('SELECT id,time FROM rounds ORDER BY id DESC LIMIT 1')
    build_round = db.get_first()[0]+1
    start_time = time.mktime(db.get_first()[1].timetuple())
    db.insert('rounds', {"id": build_round})
    db.action('SUB_REDDITS', 'SELECT', ['name', 'id'])
    results = db.get_results()
    now = time.time()
    for res in results:
        print('STARTING: {}'.format(res[0]))
        posts = __get_posts(res[0], now, start_time)
        comments = __get_comments(res[0], now, start_time)
        num_posts = len(posts)
        score_posts = 0
        for p in posts:
            score_posts += p['score']
        num_comments = len(comments)
        score_comments = 0
        for c in comments:
            score_comments += c['score']
        ins = {}
        ins['quantity_posts'] = num_posts
        ins['posts_score'] = score_posts
        ins['quantity_comments'] = num_comments
        ins['comments_score'] = score_comments
        ins['round_id'] = build_round
        ins['subreddit_id'] = res[1]
        db.insert('SUB_REDDIT_DATA', ins)
    print(time.time()-beginning)
