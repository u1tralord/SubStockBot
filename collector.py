__author__ = 'alexthomas'

import praw
import time
import json
import requests
from wrappers.DB import DB

def get_json(path,after=None):
    url = 'http://www.reddit.com/{}.json?limit=25'.format(path)
    if (after):
        url += '&after=' + after
    r = requests.get(url, headers={'user-agent': 'sub_stock_bot/0.0.1'})
    data = r.json()
    return data


def get_all(path,start_time,end_time):
    results = []
    run = True
    after = None
    while run:
        try:
            data = get_json(path,after)['data']
            after = data['after']
            for child in data['children']:
                child = child['data']
                if start_time < child['created_utc'] < end_time:
                    results.append(child)
                else:
                    run = False
        except Exception as e:
           print(e)
        if not after:
            run = False
    return results


def get_posts(sub_reddit,now,T=86400):
    end_time = now
    start_time = now-T
    path = 'r/{}/new'.format(sub_reddit)
    return get_all(path,start_time,end_time)

def get_comments(sub_reddit,now,T=86400):
    end_time = now
    start_time = now-T
    path = 'r/{}/comments'.format(sub_reddit)
    return get_all(path,start_time,end_time)




def collect():
    db = DB()
    db.query('SELECT id FROM rounds ORDER BY id DESC LIMIT 1')
    build_round = db.get_first()[0]+1
    db.insert('rounds',{"id":build_round})
    db.action('SUB_REDDITS','SELECT',['name','quantity_posts','posts_score','quantity_comments','comments_score','id'])
    results = db.get_results()
    now = time.time()
    for res in results:
        print('STARTING: {}'.format(res[0]))
        posts = get_posts(res[0],now)
        comments = get_comments(res[0],now)
        num_posts = len(posts)
        score_posts = 0
        for p in posts:
            score_posts += p['score']
        num_comments = len(comments)
        score_comments = 0
        for c in comments:
            score_comments += c['score']
        ins = {}
        ins['change_quantity_posts'] = num_posts - res[1]
        ins['change_posts_score'] = score_posts - res[2]
        ins['change_quantity_comments'] = num_comments - res[3]
        ins['change_comments_score'] = score_comments - res[4]
        ins['round_id']=build_round
        ins['subreddit_id'] = res[5]
        db.insert('changes', ins)
        db.update('SUB_REDDITS',{"quantity_posts":num_posts,"posts_score":score_posts,"quantity_comments":num_comments,"comments_score":score_comments},('id','=',str(res[5])))
