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
    tw = re.sub("[^a-zA-Z0-9,?!%&' ]", "", tw)
    tw = re.sub("%AT%", "@", tw)
    tw = re.sub("%ELLIPSE% ?", " ... ", tw)
    tw = re.sub(" ?%AMPERSAND% ?", " & ", tw)
    tw = re.sub("%HYPHEN%", "-", tw)
    tw = re.sub("%TAG%", " #", tw)
    last = tw[-5:].strip()  # check to see if we need to add a period
    if "..." not in last and "?" not in last and "!" not in last and "." not in last:
        tw += " . "
    return tw


def add_to_dict():
    for word in words.split(" "):
        word = word.strip().lower()
        if word != "":
            if word in dictionary:  # keep count
                dictionary[word] += 1
            else:
                dictionary[word] = 1


def useless(tw):
    return tw["is_retweet"] or "Donald Trump" in tw["text"]


def most_used_words():
    i = 0  # ranking of word frequency
    x_list = []
    y_list = []
    # summ = 0
    for key, value in sorted(dictionary.iteritems(), reverse=True, key=lambda (k, v): (v, k)):
        i += 1
        x_list.append(i)
        y_list.append(value)
        if value > 3:  # ignore words used less than four times
            print "%d - %s: %s" % (i, key, value)
            # summ += value


def generate_corpus():
    out_num = open("numeric_corpus.txt", 'wb')
    out_word = open("verbal_corpus.txt", 'wb')
    for word in full_corpus.split(" "):
        if word != "":
            try:
                count = dictionary[word.lower()]
                output = str(count) + "\n" if count >= 4 else "0" + "\n"

            except:
                output = str(0) + "\n"  # this word has less than 4 occurrences
            out_num.write(output)
            out_word.write(word + "\n")
    out_num.close()
    out_word.close()


# main
dictionary = dict()  # keep count
full_corpus = []
with open("corpus.json", 'rb') as corpus:
    tweets = json.loads(corpus.read())
for tweet in tweets:
    if useless(tweet):  # ignore third person
        continue
    words = clean(tweet["text"])
    add_to_dict()
    full_corpus.append(words)

full_corpus = "".join(full_corpus)  # assemble into singe blob of text
generate_corpus()
print "done"


### visual analysis
# R commands
# input <- read.csv("/Users/matthew/Desktop/College/Junior/CS/CS540HW5/WARC201709/outfile.csv",header = TRUE)
# plot(c(1:dim(input)[1]),log(input[,1]),
#      xlab = "Word Rank", ylab = "Word Frequency", main = "Plot: Word Rank vs Frequency", col = "darkred")
# plot(c(1:dim(input)[1]),log(input[,1]),
#      xlab = "Word Rank", ylab = "Word Frequency (ln)", main = "Plot: Word Rank vs Frequency (ln)", col = "darkred")
