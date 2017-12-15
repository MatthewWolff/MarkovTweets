import json
import os
import re
from os import listdir
from os.path import isfile, join


def clean(text):
    tw = text
    tw = re.sub("(https?://.*)|(www\..*)|(t\.co.*)|(amzn\.to.*)( |$)", "", tw)  # remove links
    tw = re.sub("RE:", "", tw)
    tw = re.sub("#", "%TAG%", tw)  # hashtagging
    tw = re.sub("Donald J\. Trump", "", tw)
    tw = re.sub("@|\.@", "%AT%", tw)  # @
    tw = re.sub("\.\.+", "%ELLIPSE%", tw)  # ellipses
    tw = re.sub("&amp;", "%AMPERSAND%", tw)
    tw = re.sub("(?<=[a-zA-Z])-(?=[a-zA-Z])", "%HYPHEN%", tw)
    tw = re.sub("(?<=[a-zA-Z])\.( |$)", " . ", tw)
    tw = re.sub("!", " ! ", tw)
    tw = re.sub("(?<=[^0-9])?,(?=[^0-9])", " , ", tw)
    tw = re.sub("\?", " ? ", tw)
    tw = re.sub("--|-", " ", tw)
    tw = re.sub("\(cont\)", "", tw)
    # tw = ''.join(ch for ch in tw if ch.isalnum() or ch is "%" or ch is " ")
    tw = re.sub("[^a-zA-Z0-9,?!% ]", "", tw)
    tw = re.sub("%AT%", "@", tw)
    tw = re.sub("%ELLIPSE%", " ... ", tw)
    tw = re.sub(" ?%AMPERSAND% ?", " & ", tw)
    tw = re.sub("%HYPHEN%", "-", tw)
    tw = re.sub("%TAG%", " #", tw)
    return tw


dictionary = dict()  # keep count
with open("corpus.json", 'rb') as corpus:
    tweets = json.loads(corpus.read())
for tweet in tweets:
    if tweet["is_retweet"] or "Donald Trump" in tweet["text"]:  # ignore third person
        continue
    words = clean(tweet["text"]).split(" ")
    for word in words:
        word = word.strip().lower()
        if word != "":
            if word in dictionary:  # keep count
                dictionary[word] += 1
            else:
                dictionary[word] = 1

i = 0
# summ = 0
x_list = []
y_list = []
# out_file = open("outfile.csv", 'wb')
for key, value in sorted(dictionary.iteritems(), reverse=True, key=lambda (k, v): (v, k)):
    i += 1
    x_list.append(i)
    y_list.append(value)
    if value > 3:
        print "%d - %s: %s" % (i, key, value)
        # summ += value
    # out_file.write(str(value) + "\n")

# print summ  # total words in corpus


### visual analysis
# R commands
# input <- read.csv("/Users/matthew/Desktop/College/Junior/CS/CS540HW5/WARC201709/outfile.csv",header = TRUE)
# plot(c(1:dim(input)[1]),log(input[,1]),
#      xlab = "Word Rank", ylab = "Word Frequency", main = "Plot: Word Rank vs Frequency", col = "darkred")
# plot(c(1:dim(input)[1]),log(input[,1]),
#      xlab = "Word Rank", ylab = "Word Frequency (ln)", main = "Plot: Word Rank vs Frequency (ln)", col = "darkred")
