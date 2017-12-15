import re
import smtplib
from datetime import datetime, timedelta
from multiprocessing import Process
from subprocess import check_output
from time import sleep, strftime

import tweepy
from keys import key, email_key  # move to other file

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
    def __init__(self, key, active_hours=range(24), hyperactive=[]):
        # authorize
        auth = tweepy.OAuthHandler(key["consumer_key"], key["consumer_secret"])
        auth.set_access_token(key["access_token"], key["access_token_secret"])
        self.api = tweepy.API(auth)
        self.me = str(self.api.me().screen_name)
        self.active = active_hours
        self.replied_tweets = "replied_tweets_%s.txt" % self.me  # custom reply file
        self.hyperactive = hyperactive

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
        username = tweet.user.screen_name
        text = tweet.full_text
        if username != self.me:  # don't respond to self
            if not is_replied(tweet):
                if "translate" in text:
                    # grab everything after the "translate:"
                    expr = re.compile(".+translate")
                    start = expr.search(text).end()
                    translated = words_to_dna(text[start:len(text)])
                    if len(translated) < 3:
                        response = "@{0} Sorry @{0}, ".format(username)
                        response += "the translation was too short. Try avoiding "
                        response += "the letters B,J,O,U,X,Z, or any emoji!"
                        error_msg = RED + "Translation for "
                        error_msg += "@%s failed - too short\n" % username + RESET
                        with open("bot_log.txt", "ab") as bot_log:
                            bot_log.write(error_msg)
                        print error_msg
                        return self.api.update_status(response, tweet.id)

                    # translated can be up 3 tweets of text... break apart and reply
                    to_tweet = divide_tweet(translated, username)
                    if to_tweet == -1:
                        response = "@{0} Sorry @{0}, ".format(username)
                        response += "the translation was too long. But congrats on "
                        response += "figuring out how to fit so many characters in!"
                        error_msg = RED + "Translation for "
                        error_msg += "@%s failed - too long\n" % username + RESET
                        with open("bot_log.txt", "ab") as bot_log:
                            bot_log.write(error_msg)
                        print error_msg
                        return self.api.update_status(response, tweet.id)

                    recent = None
                    for new_tweet in to_tweet:
                        with open("bot_log.txt", "ab") as bot_log:
                            bot_log.write("translated " + new_tweet + "\n")
                        print YELLOW + "translated " + BOLDWHITE + new_tweet + RESET
                        recent = self.api.update_status(status=new_tweet,
                                                        in_reply_to_status_id=(tweet.id
                                                                               if recent is None
                                                                               else recent.id))
                else:  # do a full convert of their handle + translate back
                    response = "@%s\n" % username
                    response += double_stranded_dna(username)
                    response += "\n(%s)" % dna_to_words(words_to_dna(username))
                    if len(response) <= TWEET_MAX_LENGTH:
                        with open("bot_log.txt", "ab") as bot_log:
                            bot_log.write("responded  " + response + "\n")
                        print YELLOW + "responded " + BOLDWHITE + response + RESET
                    else:
                        response = "@%s, your handle is too long!\n" % username
                        response += "Try doing a custom translation instead, by tw"
                        response += "eeting at me using the keyword \"translate\"?"
                        error_msg = RED + "Translation for "
                        error_msg += "@%s failed - handle too long\n" % username + RESET
                        with open("bot_log.txt", "ab") as bot_log:
                            bot_log.write(error_msg)
                        print error_msg
                    return self.api.update_status(response, tweet.id)

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


if __name__ == '__main__':
    bot = MarkovBot(key)
    print bot.is_active()
