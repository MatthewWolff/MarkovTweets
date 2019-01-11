#!/usr/bin/env python
import sys
from time import sleep
from random import random

from MarkovBot import MarkovBot
from keys import keys

TWEET_MAX_LENGTH = 280

"""
NOTE: for smaller tweet bodies, lower the min_word_freq to get more realistic (but less original) tweets
"""
argc = len(sys.argv)
bot = MarkovBot(keys["MarkovSports"], "AdamSchefter", max_chains=5, min_word_freq=2, active_hours=range(7, 21))

while True:
    if bot.is_active():
        twt = bot.tweet_chain(max_length=90, safe=True)
        print twt

    tweet_offset = (1 - random() * 2) * 60 * 30  # up to a half hour in either direction == waits 0.5-1.5 hours
    # print tweet_offset + 3600
    sleep(60*60 + tweet_offset)  # sleep for an hour or so

