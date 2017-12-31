import sys

from MarkovBot import MarkovBot
from keys import keys

TWEET_MAX_LENGTH = 280

argc = len(sys.argv)
handle = "johnbolka" if argc is 1 else "".join(sys.argv[1:]).strip().replace(" ", "")
# NOTE: for smaller tweet bodies, lower the min_word_freq to get more realistic (but less original) tweets
bot = MarkovBot(keys["MarkovChainer"], handle, seed=1893-7-19, max_chains=4, min_word_freq=1)
# , scrape_from="2017-12-01")
for __ in xrange(20):
    twt = bot.chain(max_length=120)
    print twt
# alt = MarkovBot(keys["MarkovRowling"], "jk_rowling",)
#
# with open("bot_files/{0}/{0}.json".format(handle)) as file:
#     text = file.read()
# import json
# text = text.replace("}, {\"contributors", "}%NEW%{\"contributors")
# tweets = text.split("%NEW%")
# print len(tweets)
# for tweet in tweets:
#     if '"text": "RT' in tweet:
#         print tweet
