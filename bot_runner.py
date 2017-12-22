import sys

from MarkovBot import MarkovBot
from keys import key

argc = len(sys.argv)
handle = "realdonaldtrump" if argc is 1 else "".join(sys.argv[1:]).strip().replace(" ", "")
bot = MarkovBot(key, handle, chain_length=4)  # generates corpus if not present
bot.regenerate(new_min_frequency=-1)
# bot.update()
# bot.set_chain(10)
bot.chain()
bot.chain()
bot.chain()
bot.chain()
bot.chain()
bot.chain()
bot.chain()

# did_it_work = bot.tweet("Hello World!")
# print did_it_work
# bot.clear_tweets()
