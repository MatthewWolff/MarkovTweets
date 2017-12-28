import sys

from MarkovBot import MarkovBot
from keys import key

TWEET_MAX_LENGTH = 280

argc = len(sys.argv)
handle = "realdonaldtrump" if argc is 1 else "".join(sys.argv[1:]).strip().replace(" ", "")
# NOTE: for smaller tweet bodies, lower the min_word_freq to get more realistic (but less original) tweets
bot = MarkovBot(key, handle, seed=1996, max_chains=4, min_word_freq=3)  # scrape_from="2017-12-01")
# bot.regenerate(new_min_frequency=3)
# bot.update(starting=)  # YYYY-MM-DD
bot.chain(max_length=120)
bot.chain(max_length=120)
bot.chain(max_length=120)
bot.chain(max_length=120)
bot.chain(max_length=120)
bot.chain(max_length=120)
bot.chain(max_length=120)
# print bot.tweet_chain(safe=True)
# print bot.tweet_chain(safe=True)
# print bot.tweet_chain(safe=True)

# did_it_work = bot.tweet("Hello World!")
# print did_it_work
# bot.clear_tweets()
