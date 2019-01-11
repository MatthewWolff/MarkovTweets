#!/usr/bin/python2.7
import json
import re

import colors


class Tokenizer:
    def __init__(self, occurrence_threshold):
        self.dictionary = dict()  # all of the words that have been used, plus their uses
        self.vocab = dict()  # the commonly used words, with index (thresholded and indexed at 1, respectively)
        self.full_corpus = []
        self.threshold = occurrence_threshold
        self.path = ""
        self.handle = ""

    # modify this for any given tweeter's idiosyncrasies... unnecessary but helps
    def specific_clean(self, text):
        if self.handle in "realdonaldtrump":
            text = re.sub("Donald J\. Trump|\(cont\)", "", text)  # realdonaldtrump, ignore when he quotes himself
        elif self.handle in "adamschefter":
            text = re.sub("([0-9]+| )(Lb|LB|lb) ?", "", text)  # adamschefter, ignore weights
        return text

    def clean(self, tweet):
        tw = self.specific_clean(tweet["text"])
        # remove @'s from replies 
        if self.handle not in "realdonaldtrump":
            tw = re.sub("^(@.+?( |$))+", "", tw)
        tw = re.sub("(https?://.*)|(www\..*)|(t\.co.*)|(amzn\.to.*)( |$)", "", tw)  # remove links
        tw = re.sub("RE:|(rt|Rt|RT) @.+ | ?RT|Rt ?|^@.+ ", "", tw)  # ignore @'s if it's a direct reply
        tw = re.sub("\.@", "@", tw)
        tw = re.sub("\n", " ", tw)
        tw = re.sub(" ?#", " #", tw)
        tw = re.sub("\.\.\.+", " ... ", tw)  # collapses long ellipses
        tw = re.sub(" ?&amp; ?", " & ", tw)  # convert into &
        tw = re.sub("(?<=[a-zA-Z])([?!.]+)( |$)", lambda x: " " + x.group(1) + " ", tw)  # punctuation
        tw = re.sub("!+", " ! ", tw)  # exclamation!! (collapses extra)
        tw = re.sub("(?<=[^0-9])?,(?=[^0-9])", " , ", tw)  # non-numeric commas
        tw = re.sub("&lt;", "<", tw)
        tw = re.sub("&gt;", ">", tw)
        tw = re.sub("\?+", " ? ", tw)  # question marks?? (collapses extra)
        tw = re.sub("--|-|[()]", " ", tw)  # replace these with spaces
        tw = re.sub("[^a-zA-Z0-9,?!%@<>;:/#&' .]", "", tw)  # remove most non alpha-numerics (including emoji)
        last = tw[-5:].strip()  # check to see if we need to add a period to their tweet
        if "..." not in last and "?" not in last and "!" not in last and "." not in last:
            tw += " . "
        return tw

    def add_to_dict(self, words):
        for word in words.split(" "):
            word = word.strip().lower()
            if word != "":
                if word in self.dictionary:  # keep count
                    self.dictionary[word] += 1
                else:
                    self.dictionary[word] = 1

    @staticmethod
    def useless(tw):
        return "Donald Trump" in tw["text"]  # ignore third person speech & retweets

    def generate_vocab(self):
        i = 0  # ranking of word frequency
        with open(self.path + "_vocab.txt", 'wb') as outfile:
            for key, value in sorted(self.dictionary.iteritems(), reverse=True, key=lambda (k, v): (v, k)):
                if value >= self.threshold:  # ignore words used less than x times
                    i += 1
                    outfile.write("{1}\n".format(i, key, value))  # ranking, word, num_use
                    self.vocab[key] = i  # basically a normalized, thresholded dictionary

    def generate_corpus(self):
        with open("{}_corpus.txt".format(self.path), 'wb') as out:
            for word in self.full_corpus.split(" "):
                if word != "":
                    try:
                        count = self.dictionary[word.lower()]
                        output = str(self.vocab[word.lower()]) + "\n" if count >= self.threshold else "0\n"
                    except KeyError:
                        output = "0\n"  # this word has less than 4 occurrences
                    out.write(output)
        with open("{}_readable_corpus.txt".format(self.path), "wb") as f:
            f.write(str(self.full_corpus))

    def process_tweets(self):
        with open("{}.json".format(self.path), 'rb') as corpus:
            tweets = json.load(corpus)
        full_corpus = []
        for tweet in tweets:
            if self.useless(tweet):
                continue
            words = self.clean(tweet)
            self.add_to_dict(words)
            full_corpus.append(words)
        self.full_corpus = "".join(full_corpus)  # assemble into singe blob of text

    def generate(self, handle, occurrence_threshold=None):  # silently creates other pieces of data
        """
        Generates the corpuses given a twitter handle
        :param handle: the handle of the account in question
        :param occurrence_threshold: the minimum number of times a word must appear in their dictionary to be in their vocab
        """
        print colors.yellow("generating corpus for {}...\n".format(handle))
        if occurrence_threshold:  # if one was given, set it
            self.threshold = occurrence_threshold
        self.handle = handle
        self.path = "bot_files/{0}/{0}".format(handle)
        self.process_tweets()
        self.generate_vocab()
        self.generate_corpus()


def generate(handle, occurrence_threshold):  # verbose, static creation
    """
    Generates the corpuses given a twitter handle
    :param handle: the handle of the account in question
    :param occurrence_threshold: the minimum number of times a word must appear in their dictionary to be in their vocab
    """
    tokenizer = Tokenizer(occurrence_threshold=occurrence_threshold)
    tokenizer.generate(handle)
    return tokenizer

# NOTE: visual analysis
# R commands
# input <- read.csv("/Users/matthew/Desktop/College/Junior/CS/CS540HW5/WARC201709/outfile.csv",header = TRUE)
# plot(c(1:dim(input)[1]),log(input[,1]),
#      xlab = "Word Rank", ylab = "Word Frequency", main = "Plot: Word Rank vs Frequency", col = "darkred")
# plot(c(1:dim(input)[1]),log(input[,1]),
#      xlab = "Word Rank", ylab = "Word Frequency (ln)", main = "Plot: Word Rank vs Frequency (ln)", col = "darkred")
