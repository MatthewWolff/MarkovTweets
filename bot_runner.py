import sys

from MarkovBot import MarkovBot
from keys import key
from markov_chains import Chain

argc = len(sys.argv)
handle = "realdonaldtrump" if argc is 1 else "".join(sys.argv[1:]).strip().replace(" ", "")
bot = MarkovBot(key, handle)  # generates corpus if not present
# bot.regenerate(new_min_frequency=3)
dick = Chain(handle=handle, max_chains=3)
dick.generate_chain()

# did_it_work = bot.tweet("Hello World!")
# print did_it_work
# bot.clear_tweets()
