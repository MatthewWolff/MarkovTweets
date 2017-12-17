from MarkovBot import MarkovBot
from keys import key
from markov_chains import Chains

handle = "johnbolka"
bot = MarkovBot(key, handle)  # generates corpus if not present
bot.regenerate(new_min_frequency=4)
dick = Chains(handle).vocab
print len(dick)

# did_it_work = bot.tweet("Hello World!")
# print did_it_work
# bot.clear_tweets()
