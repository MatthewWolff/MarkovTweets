import sys

from MarkovBot import MarkovBot
from keys import key

argc = len(sys.argv)
handle = "test" if argc is 1 else "".join(sys.argv[1:]).strip().replace(" ", "")
bot = MarkovBot(key, handle)  # generates corpus if not present
# bot.regenerate(new_min_frequency=3)
# bot.update()
bot.chain()
bot.chain()
bot.set_chain(max_chains=5)
bot.chain()

# did_it_work = bot.tweet("Hello World!")
# print did_it_work
# bot.clear_tweets()
