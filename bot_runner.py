import sys

from MarkovBot import MarkovBot
from keys import keys

TWEET_MAX_LENGTH = 280

argc = len(sys.argv)
handle = "realdonaldtrump" if argc is 1 else "".join(sys.argv[1:]).strip().replace(" ", "")
# NOTE: for smaller tweet bodies, lower the min_word_freq to get more realistic (but less original) tweets
bot = MarkovBot(keys["MarkovChainer"], handle, seed=1996, max_chains=2, min_word_freq=2)  # , scrape_from="2017-12-01")
for __ in xrange(10):
    bot.chain(max_length=120)
# alt = MarkovBot(keys["MarkovRowling"], "jk_rowling",)
# for __ in xrange(10):
#     alt.chain(max_length=120)

# did_it_work = bot.tweet("Hello World!")
# print did_it_work
# bot.clear_tweets()
