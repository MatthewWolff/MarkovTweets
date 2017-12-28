import json
import os
import re
import smtplib
import subprocess
import sys
import urllib2  # for querying data to scrape
from datetime import datetime
from threading import Thread
from time import sleep, strftime

import colors
import tweepy
from MarkovChains import Chain
from Tokenizer import Tokenizer, generate
from bs4 import BeautifulSoup
from keys import email_key
from tweepy import TweepError
from twitter_scraping.get_metadata import build_json
from twitter_scraping.scrape import scrape

"""
This is a bot that uses markov chaining to generate tweets when given a twitter user's handle
It is particularly efficient in its analysis of the corpus.
Using http://trumptwitterarchive.com/ as the original source of tweets from the president (includes deleted).
Partially inspired by https://boingboing.net/2017/11/30/correlation-between-trump-twee.html
"""
# constants
TWEET_MAX_LENGTH = 280
MIN_TWEET_LENGTH = 30  # arbitrary


class MarkovBot:
    def __init__(self, api_key, other_handle, active_hours=range(24), max_chains=5,
                 min_word_freq=3, seed=None, scrape_from=None):
        self.active = active_hours  # NOTE:limited use rn
        self.api, self.me, self.handle, self.fancy_handle = self.verify(api_key, other_handle)
        self.folder = "bot_files/{0}/".format(self.handle)
        self.log = self.folder + "{0}_log.txt".format(self.handle)
        self.corpus = self.folder + "{0}.json".format(self.handle)
        self.replied_tweets = self.folder + "{0}_replied_tweets.txt".format(self.handle)  # custom reply file
        self.tokenizer = self.check_corpus(scrape_from, min_word_freq)
        self.chain_maker = Chain(self.handle, max_chains=max_chains, seed=seed)

    def verify(self, api_key, handle):
        """
        Verifies that the user has valid credentials for accessing Tweepy API
        :param api_key: a python dictionary object containing a "consumer_key","consumer_secret","access_token"
            and "access_token_secret", in no particular order
        :param handle: the handle of the twitter user that the bot operator wishes to mimic
        :return: a 4-tuple of an API object, the bot's handle, the standardized handle of the other user, and the
            actual handle of the other user (can have uppercase letters)
        """
        sys.stdout.write(colors.yellow("verifying credentials"))
        thread = Thread(target=self.loading())  # lol
        thread.daemon = True  # kill this thread if program exits
        thread.start()
        auth = tweepy.OAuthHandler(api_key["consumer_key"], api_key["consumer_secret"])
        auth.set_access_token(api_key["access_token"], api_key["access_token_secret"])
        api = tweepy.API(auth)
        handle = handle.strip().lower()  # standardize name formatting for folder name
        try:
            # test that API works
            who_am_i = handle if handle in "test" else api.get_user(handle).screen_name
            me = api.me().screen_name
        except TweepError as e:
            err = e[:][0][0]["message"]
            raise ValueError("Awh dang dude, you gave me something bad: {}".format(err))
        thread.join()  # lol
        print colors.white(" verified")
        print colors.cyan("starting up bot ") + colors.white("@" + me) + colors.cyan(" as ") + colors.white(
            "@" + who_am_i) + colors.cyan("!\n")
        return api, me, handle, who_am_i  # api, the bot's name, the other user's name, full version of user's name

    def check_corpus(self, scrape_from_when, min_word_freq):
        """
        Checks if there are pre-existing files or if they will have to be regenerated. If data needs to be scraped
        the bot will go ahead and do that and immediately generate a corpus for the collected data.
        :type min_word_freq: the minimum number of times a word must appear in the corpus to be in the user's vocab
        :param scrape_from_when: When the bot will start grabbing tweets from
        """
        if min_word_freq < 1:
            raise ValueError(colors.red("Word frequency threshold must be greater than 0"))

        scraped = False
        if not os.path.exists(self.corpus):  # check for corpus file
            print colors.red("no corpus.json file found - generating...")
            if not os.path.exists(self.folder):  # check if they even have a folder yet
                os.mkdir(self.folder)
            scrape(self.handle, start=scrape_from_when if scrape_from_when else self.get_join_date())
            build_json(self.api, handle=self.handle)
            scraped = True
        if scrape_from_when and not scraped:  # they already had a corpus and need a special scrape
            scrape(self.handle, start=scrape_from_when)
            build_json(self.api, handle=self.handle)
        if not os.path.exists(self.folder + "%s_corpus.txt" % self.handle) or not os.path.exists(
                        self.folder + "%s_vocab.txt" % self.handle):
            return Tokenizer(min_word_freq).generate(self.handle)
        # always return the Tokenizer object
        return None if self.handle in "test" else Tokenizer(min_word_freq).generate(self.handle)

    def update(self, starting=None):
        """
        By default, checks "{usr}_all_ids.json" for when tweets were most recently scraped, then scrapes from then until
        the present. If no tweets were collected or not file was found, begins scraping from their join date.
        :param starting: The date to start scraping from (FORMAT: YYYY-MM-DD)
        """
        if not starting:  # if not given, look from beginnign
            starting = self.get_join_date()
        print colors.cyan("Updating corpus.json")
        scrape(self.handle, start=starting)

    def chain(self, max_length=TWEET_MAX_LENGTH):
        """
        Generates and prints a sentence using Markov chains. User can specify the maximum length of the tweet lest it
        defaults to the maximum tweet length
        :param max_length: the maximum number of characters allowed in the tweet - by default, max tweet length
        :return: the markov chain text that was generated
        """
        if max_length < MIN_TWEET_LENGTH:
            raise ValueError(colors.red("Tweets must be larger than {} chars".format(MIN_TWEET_LENGTH)))
        chain_text = self.chain_maker.generate_chain(max_length)
        print colors.white("@" + self.fancy_handle) + colors.yellow(" says: ") + chain_text
        return chain_text

    def tweet_chain(self, max_length=TWEET_MAX_LENGTH, safe=False):
        """
        Bot issues a tweet made by markov chaining
        :param max_length: the maximum number of characters allowed in the tweet - by default, max tweet length
        :param safe: if True, bot will remove all "@" symbols so that twitter doesn't get mad :(
        :return: the text of the tweet that was tweeted
        """
        tweet_text = self.chain_maker.generate_chain(max_length=max_length)
        if safe:
            tweet_text = tweet_text.replace("@", "#")  # :(
        self.tweet(tweet_text)
        return tweet_text

    @staticmethod  # hehe
    def loading():
        for x in [".", ".", "."]:
            sys.stdout.write(colors.yellow(x))
            sys.stdout.flush()
            sleep(0.5)

    def get_join_date(self):
        """
        Helper method - checks a user's twitter page for the date they joined
        :return: the "%day %month %year" a user joined
        """
        page = urllib2.urlopen("https://twitter.com/" + self.handle)
        soup = BeautifulSoup(page, "html.parser")
        date_string = str(soup.find("span", {"class": "ProfileHeaderCard-joinDateText"})["title"]).split(" - ")[1]
        date_string = str(0) + date_string if date_string[1] is " " else date_string
        return str(datetime.strptime(date_string, "%d %b %Y"))[0:10]

    def regenerate(self, new_min_frequency):  # change threshold - convenience method ig
        """
        Regenerates the corpus with a non-default minimum word frequency
        :param new_min_frequency: the minimum number of times a word must appear in the corpus to be in the vocab
        """
        if new_min_frequency < 1:
            raise ValueError(colors.red("Word frequency threshold must be greater than 0"))
        print colors.yellow("regenerating vocab with required min frequency at {}...\n".format(new_min_frequency))
        self.tokenizer.generate(self.handle, new_min_frequency)

    def tweet(self, tweet=None, at=None):
        """
        General tweeting method. It will divide up long bits of text into multiple messages, and return the first tweet
        that it makes. Multi-tweets (including to other people) will have second and third messages made in response
        to self.
        :param at: who the user is tweeting at
        :param tweet: the text to tweet
        :return: the first tweet if successful, else None
        """
        if not tweet:
            return None

        num_tweets, tweets = self.divide_tweet(tweet, at)
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
                print colors.white("deleted successfully")
            except tweepy.TweepError:
                print colors.red("Failed to delete:"), status.id

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
        print(colors.cyan("Beginning polling...\n"))
        while 1:
            try:
                for tweet in tweepy.Cursor(self.api.search, q='@{0} -filter:retweets'.format(self.me),
                                           tweet_mode="extended").items():
                    respond(tweet)
            except tweepy.TweepError as e:
                print RED + e.api_code + RESET

            sleep(30)
