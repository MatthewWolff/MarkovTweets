import datetime
import json
import os
import urllib2  # for querying data to scrape
from time import sleep

import colors
import requests
from bs4 import BeautifulSoup
from get_metadata import build_json
from requests_oauthlib import OAuth1
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from selenium.webdriver.common.keys import Keys

"""
Credit for selenium scraping goes to https://github.com/bpb27/twitter_scraping
I took the source code and modified to jump through months instead of day by day. Silenced some outputs, too.
Added in command line args
"""


def has_less_than_3200(username):
    page = urllib2.urlopen("https://twitter.com/" + username)
    soup = BeautifulSoup(page, "html.parser")
    nav_elems = soup.findAll("span", {"class": "ProfileNav-label"})
    for elem in nav_elems:
        if elem.text in "Tweets":
            return int(elem.next_sibling.next_sibling.next_sibling.next_sibling["data-count"]) <= 3200
    raise ValueError("This user is either private or simply hasn't tweeted")


def make_tweet(tweet):
    return {
        "text": tweet["text"],
        "retweet_count": tweet["retweet_count"],
        "favorite_count": tweet["favorite_count"],
        "id_str": tweet["id_str"],
        "is_retweet": "retweet_status" in tweet,
        "is_reply": tweet["in_reply_to_status_id"] if tweet["in_reply_to_status_id"] is not None else None,
    }


def generate_json(username, keys):
    username = username.lower()
    auth = OAuth1(keys["consumer_key"], keys["consumer_secret"], keys["access_token"], keys["access_token_secret"])
    number = 3200
    api_url = "https://api.twitter.com/1.1/statuses/user_timeline.json?screen_name="
    url = api_url + "{}&count={}".format(username, number)
    r = requests.get(url, auth=auth)
    tweets = []
    if r.status_code == 200:
        for tweet_json in r.json():
            tweets.append(tweet_json)
    else:
        raise Exception("there was an issue with retrieval: %s" % r.status_code)

    # Getting the additional pages after the first
    last_id = tweets[len(tweets) - 1]["id"]
    curr_id = tweets[len(tweets) - 2]["id"]  # the last tweet, aka the next one to start with
    counter = 0
    max_counter = 100  # (Max API calls for testing, increase later)
    # Looping through pages of tweets until there are no new available or API limit is exceeded
    while last_id < curr_id and counter < max_counter:
        curr_id = last_id
        url = api_url + "{}&count={}&max_id={}".format(username, number, curr_id - 1)
        r = requests.get(url, auth=auth)
        if r.status_code == 200:
            for tweetjson in r.json():
                tweets.append(tweetjson)
        else:
            handleHTTPErrorCode(r.status_code)
        last_id = tweets[len(tweets) - 1]["id"]
        counter += 1

    print "%s tweets found" % len(tweets)
    results = []
    for entry in tweets:
        results.append(make_tweet(entry))

    if not os.path.exists("bot_files/%s" % username):
        os.mkdir("bot_files/%s" % username)
    with open("bot_files/{0}/{0}.json".format(username), "wb") as outfile:
        json.dump(results, outfile)


def format_day(date):
    day = "0" + str(date.day) if len(str(date.day)) == 1 else str(date.day)
    month = "0" + str(date.month) if len(str(date.month)) == 1 else str(date.month)
    year = str(date.year)
    return "-".join([year, month, day])


def form_url(user, since, until):
    p1 = "https://twitter.com/search?f=tweets&vertical=default&q=from%3A"
    p2 = user + "%20since%3A" + since + "%20until%3A" + until + "include%3Aretweets&src=typd"
    return p1 + p2


def increment_day(date, i):
    return date + datetime.timedelta(days=i)


def scrape(user, api, start, end=datetime.datetime.now()):
    """
    If the user has less than 3200 tweets total, the start and end paramters will be ignored
    :param user: the handle of the user you're trying to scrape
    :param api: an API key object
    :param start: the date to start scraping
    :param end: the date to end scraping
    """
    user = user.lower()  # pass in twitter handle
    year, month, day = (int(x) for x in start.split("-"))
    start = datetime.datetime(year, month, day)  # year, month, day
    if has_less_than_3200(user):
        print colors.yellow("\nuser has less than 3200 tweets, doing simple scrape...")
        generate_json(user, api)
        return 0

    # only edit these if you're having problems
    delay = 1  # time to wait on each page load before reading the page
    driver = webdriver.Chrome()  # options are Chrome() Firefox() Safari()

    # don't mess with this stuff
    twitter_ids_filename = "bot_files/{0}/{0}_all_ids.json".format(user)
    if os.path.exists(twitter_ids_filename):
        with open(twitter_ids_filename) as f:
            start = str(json.load(f)["most_recent"])
            year, month, day = (int(x) for x in start.split("-"))
            start = datetime.datetime(year, month, day)

    days = (end - start).days + 1
    id_selector = ".time a.tweet-timestamp"
    tweet_selector = "li.js-stream-item"
    ids = []
    print(colors.cyan("\tscraping from {} to present".format(str(start)[:10])))
    by = 31  # month at a time
    for __ in range(days)[::by]:
        d1 = format_day(increment_day(start, 0))
        d2 = format_day(increment_day(start, by))
        url = form_url(user, d1, d2)
        # print(url)
        # print(d1)
        driver.get(url)
        sleep(delay)

        try:
            found_tweets = driver.find_elements_by_css_selector(tweet_selector)
            increment = 10

            while len(found_tweets) >= increment:
                # print("scrolling down to load more tweets")
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                sleep(delay)
                found_tweets = driver.find_elements_by_css_selector(tweet_selector)
                increment += 10

            # print("{} tweets found, {} total".format(len(found_tweets), len(ids)))

            for tweet in found_tweets:
                try:
                    id = tweet.find_element_by_css_selector(id_selector).get_attribute("href").split("/")[-1]
                    ids.append(id)
                except StaleElementReferenceException:
                    print colors.red("lost element reference"), tweet
        except NoSuchElementException:
            print colors.red("no tweets on this day")

        start = increment_day(start, by)

    most_recent = datetime.datetime.now().strftime("%Y-%m-%d")[:10]
    try:  # attempts to reconcile new tweets with old
        with open(twitter_ids_filename) as f:
            all_ids = ids + json.load(f)["ids"]
            data_to_write = {"ids": list(set(all_ids)), "most_recent": most_recent}
    except IOError:  # if fails, just writes
        all_ids = ids
        data_to_write = {"ids": list(set(all_ids)), "most_recent": most_recent}

    with open(twitter_ids_filename, 'wb') as outfile:
        json.dump(data_to_write, outfile)

    print(colors.cyan("found {} tweets\n".format(len(data_to_write["ids"]))))
    driver.close()
    build_json(user, api)
    return 0
