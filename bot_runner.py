import sys

from MarkovBot import MarkovBot
from keys import keys

TWEET_MAX_LENGTH = 280

"""
NOTE: for smaller tweet bodies, lower the min_word_freq to get more realistic (but less original) tweets
"""
argc = len(sys.argv)
handle = "adamschefter" if argc is 1 else "".join(sys.argv[1:]).strip().replace(" ", "")
bot = MarkovBot(keys["MarkovChainer"], handle, seed=1893-7-19, max_chains=3, min_word_freq=2)
# , scrape_from="2017-12-01")
for __ in xrange(30):
    twt = bot.chain(max_length=120)
    print twt
