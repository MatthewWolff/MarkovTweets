import os
import re
import smtplib
import subprocess
import urllib2  # for querying data to scrape
from datetime import datetime
from time import sleep, strftime

import tweepy
from Tokenizer import Tokenizer, generate
from bs4 import BeautifulSoup
from keys import email_key
from twitter_scraping.get_metadata import build_json
from twitter_scraping.scrape import scrape

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


class MarkovBot:
    def __init__(self, api_key, other_handle, active_hours=range(24)):
        # authorize
        auth = tweepy.OAuthHandler(api_key["consumer_key"], api_key["consumer_secret"])
        auth.set_access_token(api_key["access_token"], api_key["access_token_secret"])
        self.api = tweepy.API(auth)
        self.me = str(self.api.me().screen_name)
        self.pretend = other_handle.lower()
        self.active = active_hours
        self.folder = "bot_files/{0}/".format(self.pretend)
        self.replied_tweets = self.folder + "{0}_replied_tweets.txt".format(self.pretend)  # custom reply file
        self.log = self.folder + "{0}_log.txt".format(self.pretend)
        self.corpus = self.folder + "{0}.json".format(self.pretend)
        self.check_corpus()

    def check_corpus(self):
        """
        Checks if there are pre-existing files or if they will have to be regenerated. If data needs to be scraped
        the bot will go ahead and do that and immediately generate a corpus for the collected data.
        """
        print "starting bot!\n"
        if not os.path.exists(self.corpus):  # scrape for their tweets
            print "no corpus.json file found - generating..."
            if not os.path.exists(self.folder):
                os.mkdir(self.folder)
            scrape(user=self.pretend, start=self.get_join_date())  # can add end date
            build_json(self.api, handle=self.pretend)
            generate(handle=self.pretend)

    def get_join_date(self):
        """
        Helper method - checks a user's twitter page for the date they joined
        :return: the "%day %month %year" a user joined
        """
        page = urllib2.urlopen("https://twitter.com/" + self.pretend)
        soup = BeautifulSoup(page, "html.parser")
        date_string = str(soup.find("span", {"class": "ProfileHeaderCard-joinDateText"})["title"]).split(" - ")[1]
        date_string = str(0) + date_string if date_string[1] is " " else date_string
        return str(datetime.strptime(date_string, "%d %b %Y"))[0:10]

    def regenerate(self, new_min_frequency):  # change threshold - convenience method ig
        """
        Regenerates the corpus with a non-default minimum word frequency
        :param new_min_frequency: the minimum number of times a word must appear in the corpus to be in the vocab
        """
        print "regenerating vocab with required min frequency at %i...\n" % new_min_frequency
        Tokenizer(occurrence_threshold=new_min_frequency).generate(self.pretend)

    def tweet(self, text=None, at=None):
        """
        General tweeting method. It will divide up long bits of text into multiple messages, and return the first tweet
        that it makes. Multi-tweets (including to other people) will have second and third messages made in response
        to self.
        :param at: who the user is tweeting at
        :param text: the text to tweet
        :return: the first tweet if successful, else None
        """
        if not text:
            return None

        num_tweets, tweets = self.divide_tweet(text, at)
        if num_tweets > 0:
            my_ret = self.api.update_status(tweets[0])
            for remaining in xrange(1, len(tweets)):
                self.api.update_status(tweets[remaining])
            return my_ret  # return first tweet - multi-tweets will be responding to it
        else:
            return None

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
                # TODO automatic response
                pass

    def divide_tweet(self, long_tweet, at=None):
        """
        A method for exceptionally long tweets
        :rtype: the number of tweets, followed by the tweets
        :param at: the person you're responding to/at
        :param long_tweet: the long-ass tweet you're trying to make
        :return: an array of up to 3 tweets
        """
        # 1 tweet
        handle = "@" + at + " " if at else ""
        my_handle = "@" + self.me
        numbered = len("(x/y) ")

        single_tweet_length = (TWEET_MAX_LENGTH - len(handle))
        first_tweet_length = (TWEET_MAX_LENGTH - len(handle) - numbered)
        self_tweet_length = (TWEET_MAX_LENGTH - len(my_handle) - numbered)
        two_tweets_length = first_tweet_length + self_tweet_length
        three_tweets_length = two_tweets_length + self_tweet_length

        # 1 tweet
        if len(long_tweet) <= single_tweet_length:
            return 1, [handle + long_tweet]
        # too many characters (edge case)
        elif len(long_tweet) >= three_tweets_length:
            return 0, None
            # 3 tweets
        elif len(long_tweet) > two_tweets_length:
            return 3, [handle + "(1/3) "
                       + long_tweet[:first_tweet_length],
                       my_handle + "(2/3) "
                       + long_tweet[first_tweet_length: two_tweets_length],
                       my_handle + "(3/3) "
                       + long_tweet[two_tweets_length: len(long_tweet)]]
        # 2 tweets
        else:
            return 2, [handle + "(1/2) "
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
