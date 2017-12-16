import os
import re
import smtplib
import subprocess
import urllib2  # for querying data to scrape
from datetime import datetime, timedelta
from multiprocessing import Process
from time import sleep, strftime

import tweepy
from Tokenizer import generate
from bs4 import BeautifulSoup
from keys import email_key  # move to other file

"""
This is a bot that uses markov chaining on the corpus of tweets made by @realDonaldDrumpf
It utilizes markov chains of up to 4 words longs.
It is particularly efficient in its analysis of the corpus.
Using http://trumptwitterarchive.com/ as the corpus.
Partially inspired by https://boingboing.net/2017/11/30/correlation-between-trump-twee.html
"""

# constants + terminal color codes
TWEET_MAX_LENGTH = 280
RED = "\033[31m"
RESET = "\033[0m"
BOLDWHITE = "\033[1m\033[37m"
YELLOW = "\033[33m"
CYAN = "\033[36m"
PURPLE = "\033[35m"
CLEAR = "\033[2J"  # clears the terminal screen


# methods
def get_date(date_string):
    """
    Helper method for determining date
    :param date_string:
    :return:
    """
    date_values = re.split("-", date_string)
    date_values = [int(i) for i in date_values]
    return datetime(date_values[0], date_values[1], date_values[2])


# move to other file
def alert(subject="Error Occurred", text="a bot has encountered an error."):
    """
    Sends an email to a specified gmail account
    :param subject: Subject
    :param text: Body of message
    """
    content = 'Subject: %s\n\n%s' % (subject, text)
    mail = smtplib.SMTP('smtp.gmail.com', 587)
    mail.ehlo()
    mail.starttls()
    mail.login(email_key["username"], email_key["password"])
    mail.sendmail(email_key["username"], email_key["destination"], content)
    mail.close()
    print(RED + "ERROR OCCURRED, EMAIL SENT" + RESET)


class MarkovBot:
    def __init__(self, api_key, other_handle, active_hours=range(24)):
        # authorize
        auth = tweepy.OAuthHandler(api_key["consumer_key"], api_key["consumer_secret"])
        auth.set_access_token(api_key["access_token"], api_key["access_token_secret"])
        self.api = tweepy.API(auth)
        self.me = str(self.api.me().screen_name)
        self.pretend = other_handle.lower()
        self.active = active_hours
        self.replied_tweets = "bot_files/%s_replied_tweets.txt" % self.pretend  # custom reply file
        self.log = "bot_files/{0}/{0}_log.txt".format(self.pretend)
        self.corpus = "bot_files/{0}/{0}.json".format(self.pretend)
        if not os.path.exists(self.pretend + self.corpus):  # scrape for their tweets
            self.scrape()

    def scrape(self):
        self._scrape_ids(self.get_join_date())
        self._meta_data()
        generate(self.pretend)

    def _scrape_ids(self, start):
        if not os.path.exists("bot_files/%s" % self.pretend):
            os.mkdir("bot_files/%s" % self.pretend)
        scrape = "python3 twitter_scraping/scrape.py {} {}".format(self.pretend, start)
        process = subprocess.Popen(scrape.split(), stdout=subprocess.PIPE)
        output, __ = process.communicate()
        print output

    def _meta_data(self):
        meta_data = "python3 twitter_scraping/get_metadata.py %s" % self.pretend
        process = subprocess.Popen(meta_data.split(), stdout=subprocess.PIPE)
        output, __ = process.communicate()
        print output

    def get_join_date(self):
        page = urllib2.urlopen("https://twitter.com/" + self.pretend)
        soup = BeautifulSoup(page, "html.parser")
        date_string = str(soup.find("span", {"class": "ProfileHeaderCard-joinDateText"})["title"]).split(" - ")[1]
        date_string = str(0) + date_string if date_string[1] is " " else date_string
        return str(datetime.strptime(date_string, "%d %b %Y"))[0:11]

    def tweet(self, text=None):
        if text:
            self.api.update_status(text)
        else:
            pass

    def clear_tweets(self):
        """
        DANGER: removes all tweets from current bot account
        """
        for status in tweepy.Cursor(self.api.user_timeline).items():
            try:
                self.api.destroy_status(status.id)
                print "deleted successfully"
            except tweepy.TweepError:
                print "Failed to delete:", status.id

    def is_replied(self, tweet):  # check if replied. if not, add to list and reply
        """
        This bot tries to reply to everyone who @'s it, so it will use a list of tweet IDs to keep track
        It is assumed that if a tweet is un-replied, the bot will reply to it (add to list)
        :param tweet: the tweet in question
        :return: if the tweet had a reply or not
        """
        with open(self.replied_tweets, "rb") as replied_tweets:
            replies = replied_tweets.readlines()
        replied = (str(tweet.id) + "\n") in replies
        if not replied:
            with open(self.replied_tweets, "ab") as replied_tweets:
                replied_tweets.write(str(tweet.id) + "\n")
        return replied

    def is_active(self):
        """
        The bot tries not to tweet at times when no one will see
        :return: whether it's late enough or not
        """
        current_time = datetime.now().hour
        early = self.active[0]
        return current_time >= early

    def respond(self, tweet):  # provide translation of custom message or username
        """
        Given a tweet, formulate a response
        :param tweet: tweet to respond to
        :return: the tweet to make in response
        """
        username = str(tweet.user.screen_name)
        text = tweet.full_text
        if username != self.me:  # don't respond to self
            if not is_replied(tweet):
                # TODO response
                pass

    def divide_tweet(self, long_tweet, username):
        """
        A method for exceptionally long tweets
        :param long_tweet: the long-ass tweet you're trying to make
        :param username: the person you're responding to
        :return: an array of up to 3 tweets
        """
        # 1 tweet
        handle = "@" + username + " "
        my_handle = "@" + self.me
        numbered = len("(x/y) ")

        single_tweet_length = (TWEET_MAX_LENGTH - len(handle))
        first_tweet_length = (TWEET_MAX_LENGTH - len(handle) - numbered)
        self_tweet_length = (TWEET_MAX_LENGTH - len(my_handle) - numbered)
        two_tweets_length = first_tweet_length + self_tweet_length
        three_tweets_length = two_tweets_length + self_tweet_length

        # 1 tweet
        if len(long_tweet) <= single_tweet_length:
            return [handle + long_tweet]
        # too many characters (edge case)
        elif len(long_tweet) >= three_tweets_length:
            return -1
            # 3 tweets
        elif len(long_tweet) > two_tweets_length:
            return [handle + "(1/3) "
                    + long_tweet[:first_tweet_length],
                    my_handle + "(2/3) "
                    + long_tweet[first_tweet_length: two_tweets_length],
                    my_handle + "(3/3) "
                    + long_tweet[two_tweets_length: len(long_tweet)]]
        # 2 tweets
        else:
            return [handle + "(1/2) "
                    + long_tweet[: first_tweet_length],
                    my_handle + "(2/2) "
                    + long_tweet[first_tweet_length: len(long_tweet)]]

    def check_tweets(self):
        """tweet upkeep multi-processing method"""
        print(CYAN + "Beginning polling...\n" + RESET)
        while 1:
            try:
                for tweet in tweepy.Cursor(self.api.search, q='@{0} -filter:retweets'.format(self.me),
                                           tweet_mode="extended").items():
                    respond(tweet)
            except tweepy.TweepError as e:
                print RED + e.api_code + RESET

            sleep(30)
