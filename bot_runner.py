from MarkovBot import MarkovBot
from Tokenizer import generate
from keys import key  # move to other file

trump = MarkovBot(key, "joshlukas97")  # generates corpus if not present
