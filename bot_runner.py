from MarkovBot import MarkovBot
from keys import key
from markov_chains import Chains

handle = "joshlukas97"
bot = MarkovBot(key, handle)  # generates corpus if not present
# bot.regenerate(new_min_frequency=3)
n1, n2, h = (int(x) for x in "0 100 414".strip().split(" "))
r = n1 / float(n2)
dick = Chains(handle, seed=20)
# dick.two_word(rand=0.292146851991, hist=12)
dick.generate_chain()


# did_it_work = bot.tweet("Hello World!")
# print did_it_work
# bot.clear_tweets()
