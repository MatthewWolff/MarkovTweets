import csv
import glob
import json
import math
import sys
import zipfile
import zlib
from time import sleep

import tweepy
from keys import key as keys
from tweepy import TweepError

"""
Credit goes to https://github.com/bpb27/twitter_scraping
I took the source code and modified it to only collect the data that I wanted. Silenced some outputs, too.
"""
# CHANGE THIS TO THE USER YOU WANT
user = sys.argv[1]  # pass in twitter handle

auth = tweepy.OAuthHandler(keys['consumer_key'], keys['consumer_secret'])
auth.set_access_token(keys['access_token'], keys['access_token_secret'])
api = tweepy.API(auth)
user = user.lower()
output_file = 'bot_files/{0}/{0}_long.json'.format(user)
output_file_short = 'bot_files/{0}/{0}.json'.format(user)
compression = zipfile.ZIP_DEFLATED

with open('bot_files/{0}/{0}_all_ids.json'.format(user)) as f:
    ids = json.load(f)

print('total tweet ids: {}'.format(len(ids)))

all_data = []
start = 0
end = 100
limit = len(ids)
i = math.ceil(limit / 100)

for go in range(i):
    print('currently getting {} - {}'.format(start, end))
    sleep(6)  # needed to prevent hitting API rate limit
    id_batch = ids[start:end]
    start += 100
    end += 100
    tweets = api.statuses_lookup(id_batch)
    for tweet in tweets:
        all_data.append(dict(tweet._json))

print('metadata collection complete!')
results = []


def get_source(entry):
    if '<' in entry["source"]:
        return entry["source"].split('>')[1].split('<')[0]
    else:
        return entry["source"]


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

print('creating json master file')
with open(output_file_short, 'w') as outfile:
    json.dump(results, outfile)
