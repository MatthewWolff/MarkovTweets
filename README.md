# MarkovTweets
Give MarkovBot a twitter handle and it can tweet like them!  
It first scrapes their entire twitter timeline (even beyond the 3200 tweet limit) by using tweepy and selenium. Once it's compiled a body of their tweets, it cleans it and tokenizes it to form the main corpus. From there, the bot uses markov chaining to produces likely tweets.

**If you're really interested, take a look at the included MarkovTweets powerpoint!**

# Requirements - Python 2.7.13
*  tweepy  
*  selenium (I use a chrome webdriver)  
*  urllib2 (for accessing pages)  
*  bs4 (from bs4 import BeautifulSoup - for a small amount of parsing)  
  
# Example  
```
starting bot!  

analyzing corpus...  
  1-chaining done  
  2-chaining done  
  3-chaining done  
  4-chaining done  
  5-chaining done  
  6-chaining done  

Beginning chain generation...  

@realdonaldtrump says: Would be a disaster in congress. Very weak on crime and illegal immigration, bad for gun owners and veterans and against the wall. Jones is a pelosi-schumer puppet. Roy moore will always vote with us. Vote roy moore!
```
