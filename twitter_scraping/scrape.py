import datetime
import json
from time import sleep

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from selenium.webdriver.common.keys import Keys

"""
Credit goes to https://github.com/bpb27/twitter_scraping
I took the source code and modified to jump through months instead of day by day. Silenced some outputs, too.
Added in command line args
"""


def format_day(date):
    day = '0' + str(date.day) if len(str(date.day)) == 1 else str(date.day)
    month = '0' + str(date.month) if len(str(date.month)) == 1 else str(date.month)
    year = str(date.year)
    return '-'.join([year, month, day])


def form_url(user, since, until):
    p1 = 'https://twitter.com/search?f=tweets&vertical=default&q=from%3A'
    p2 = user + '%20since%3A' + since + '%20until%3A' + until + 'include%3Aretweets&src=typd'
    return p1 + p2


def increment_day(date, i):
    return date + datetime.timedelta(days=i)


def scrape(user, start, end=datetime.datetime.now()):
    user = user.lower()  # pass in twitter handle
    year, month, day = (int(x) for x in start.split("-"))
    start = datetime.datetime(year, month, day)  # year, month, day

    # only edit these if you're having problems
    delay = 1  # time to wait on each page load before reading the page
    driver = webdriver.Chrome()  # options are Chrome() Firefox() Safari()

    # don't mess with this stuff
    twitter_ids_filename = 'bot_files/{0}/{0}_all_ids.json'.format(user)
    days = (end - start).days + 1
    id_selector = '.time a.tweet-timestamp'
    tweet_selector = 'li.js-stream-item'
    ids = []

    print("Scraping from {} to present".format(str(start)[:10]))
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
                # print('scrolling down to load more tweets')
                driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
                sleep(delay)
                found_tweets = driver.find_elements_by_css_selector(tweet_selector)
                increment += 10

            # print('{} tweets found, {} total'.format(len(found_tweets), len(ids)))

            for tweet in found_tweets:
                try:
                    id = tweet.find_element_by_css_selector(id_selector).get_attribute('href').split('/')[-1]
                    ids.append(id)
                except StaleElementReferenceException:
                    print('lost element reference', tweet)
        except NoSuchElementException:
            print('no tweets on this day')

        start = increment_day(start, by)

    try:  # attempts to reconcile new tweets with old
        with open(twitter_ids_filename) as f:
            all_ids = ids + json.load(f)
            data_to_write = list(set(all_ids))
    except IOError:  # if fails, just writes
        all_ids = ids
        data_to_write = list(set(all_ids))

    with open(twitter_ids_filename, 'w') as outfile:
        json.dump(data_to_write, outfile)

    print("found {} tweets\n".format(len(data_to_write)))
    driver.close()
