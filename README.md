# PresidentMarkov
[WORK IN PROGRESS]   
Give MarkovBot a twitter handle and it can tweet like them!  
It first scrapes their entire twitter timeline (even beyond the 3200 tweet limit) by using tweepy and selenium. Once it's compiled a body of their tweets, it cleans it and tokenizes it to form the main corpus. From there, the bot uses markov chaining to produces likely tweets.

# Requirements - Python 2.7.13
..*  tweepy
..*  selenium (I use a chrome webdriver)
..*  urllib2 (for accessing pages)
..*  bs4 (from bs4 import BeautifulSoup - for a small amount of parsing)
