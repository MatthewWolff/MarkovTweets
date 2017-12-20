# PresidentMarkov
[WORK IN PROGRESS]   
Give MarkovBot a twitter handle and it can tweet like them!  
It first scrapes their entire twitter timeline (even beyond the 3200 tweet limit) by using tweepy and selenium. Once it's compiled a body of their tweets, it cleans it and tokenizes it to form the main corpus. From there, the bot uses markov chaining to produces likely tweets.

# Requirements - Python 2.7.13
*  tweepy  
*  selenium (I use a chrome webdriver)  
*  urllib2 (for accessing pages)  
*  bs4 (from bs4 import BeautifulSoup - for a small amount of parsing)  
  
# Example  
starting bot!  
&nbsp;&nbsp;  
analyzing corpus...  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;1-chaining done  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;2-chaining done  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;3-chaining done  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;4-chaining done  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;5-chaining done  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;6-chaining done  
&nbsp;    
Beginning chain generation...  
&nbsp;    
@realdonaldtrump says: Would be a disaster in congress. Very weak on crime and illegal immigration, bad for gun owners and veterans and against the wall. Jones is a pelosi-schumer puppet. Roy moore will always vote with us. Vote roy moore!
