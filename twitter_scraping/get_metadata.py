import glob
import json
import math
import sys
from time import sleep

import tweepy
from tweepy import TweepError

"""
Credit goes to https://github.com/bpb27/twitter_scraping
I took the source code and modified it to only collect the data that I wanted. Silenced some outputs, too.
"""


def get_source(entry):
    if '<' in entry["source"]:
        return entry["source"].split('>')[1].split('<')[0]
    else:
        return entry["source"]


def build_json(api, handle):
    print 'beginning meta_data collection...'
    user = handle.lower()
    output_file = 'bot_files/{0}/{0}.json'.format(user)

    with open('bot_files/{0}/{0}_all_ids.json'.format(user)) as f:
        ids = json.load(f)

    # print('total tweet ids: {}'.format(len(ids)))

    all_data = []
    start = 0
    end = 100
    limit = len(ids)
    i = int(math.ceil(limit / 100))

    for go in range(i):
        print('currently getting {} - {}'.format(start, end))
        sleep(6)  # needed to prevent hitting API rate limit
        id_batch = ids[start:end]
        start += 100
        end += 100
        tweets = api.statuses_lookup(id_batch)
        for tweet in tweets:
            all_data.append(dict(tweet._json))

    results = []

    for entry in all_data:
        t = {
            # "created_at": entry["created_at"],
            "text": entry["text"],
            # "in_reply_to_screen_name": entry["in_reply_to_screen_name"],
            "retweet_count": entry["retweet_count"],
            "favorite_count": entry["favorite_count"],
            # "source": get_source(entry),
            "id_str": entry["id_str"],
            "is_retweet": entry["retweeted"]
        }
        results.append(t)

    print('metadata collection complete!\n')
    print('creating json master file\n')
    with open(output_file, 'w') as outfile:
        json.dump(results, outfile)
