import glob
import json
import math
import os
from time import sleep

import colors
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


def make_tweet(tweet):
    return {
        "text": tweet["text"],
        "retweet_count": tweet["retweet_count"],
        "favorite_count": tweet["favorite_count"],
        "id_str": tweet["id_str"],
        "is_retweet": "retweet_status" in tweet,
        "is_reply": tweet["in_reply_to_status_id"] if tweet["in_reply_to_status_id"] is not None else None,
    }


def build_json(user, api):
    print colors.yellow("beginning meta_data collection...")
    user = user.lower()
    auth = tweepy.OAuthHandler(api["consumer_key"], api["consumer_secret"])
    auth.set_access_token(api["access_token"], api["access_token_secret"])
    api = tweepy.API(auth)
    output_file = "bot_files/{0}/{0}.json".format(user)

    with open("bot_files/{0}/{0}_all_ids.json".format(user)) as f:
        ids = json.load(f)["ids"]

    all_data = []
    start = 0
    end = 100
    limit = len(ids)
    i = int(math.ceil(limit / 100.0))

    for go in range(i):
        print colors.cyan("currently getting {} - {}".format(start, end))
        sleep(6)  # needed to prevent hitting API rate limit
        id_batch = ids[start:end]
        start += 100
        end += 100
        tweets = api.statuses_lookup(id_batch)
        for tweet in tweets:
            all_data.append(dict(tweet._json))

    results = []
    for entry in all_data:
        results.append(make_tweet(entry))

    print colors.cyan("metadata collection complete!\n")

    if len(results) is 0:
        raise EmptyCorpusException("Error: No tweets were collected.")

    print colors.yellow("creating json file...\n")
    with open(output_file, 'wb') as outfile:
        json.dump(results, outfile)
        import os
        os.system("say done")  # spooky


class EmptyCorpusException(Exception):
    def __init__(self, *args):
        Exception.__init__(self, *args)
