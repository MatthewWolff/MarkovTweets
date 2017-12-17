from MarkovBot import MarkovBot
from keys import key  # move to other file

bot = MarkovBot(key, "thednabot")  # generates corpus if not present
print bot.is_active()
# did_it_work = bot.tweet("Hello World!")
# print did_it_work
# bot.clear_tweets()
