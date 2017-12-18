#!/usr/bin/python2.7
import json
import re


class Tokenizer:
    def __init__(self, occurrence_threshold=4):
        self.dictionary = dict()  # all of the words that have been used, plus their uses
        self.full_corpus = []
        self.threshold = occurrence_threshold
        self.path = ""
        self.vocab = dict()  # the commonly used words, with index (thresholded and indexed at 1, respectively)

    @staticmethod
    def clean(text):
        tw = text
        tw = re.sub("(https?://.*)|(www\..*)|(t\.co.*)|(amzn\.to.*)( |$)", "", tw)  # remove links
        tw = re.sub("RE:", "", tw)
        tw = re.sub("Donald J\. Trump", "", tw)
        tw = re.sub("#", "%TAG%", tw)  # hashtagging
        tw = re.sub("@|\.@", "%AT%", tw)  # @, note: it gets rid of .@'s
        tw = re.sub("\.\.\.+", "%ELLIPSE%", tw)  # collapses long ellipses
        tw = re.sub("&amp;", "%AMPERSAND%", tw)  # convert into &
        tw = re.sub("(?<=[a-zA-Z])-(?=[a-zA-Z])", "%HYPHEN%", tw)
        tw = re.sub("(?<=[a-zA-Z])\.( |$)", " . ", tw)  # punctuation
        tw = re.sub("!+", " ! ", tw)  # exclamation (collapses)
        tw = re.sub("(?<=[^0-9])?,(?=[^0-9])", " , ", tw)  # non-numeric commas
        tw = re.sub("\?+", " ? ", tw)  # question marks?? (collapses)
        tw = re.sub("\(cont\)", "", tw)  # who does this lmao
        tw = re.sub("--|-|[()<>]", " ", tw)  # replace these with spaces
        tw = re.sub("[^a-zA-Z0-9,?!%&' .]", "", tw)  # replace most non alpha-numerics with nothing
        # re-instate
        tw = re.sub("%AT%", "@", tw)
        tw = re.sub("%ELLIPSE% ?", " ... ", tw)
        tw = re.sub(" ?%AMPERSAND% ?", " & ", tw)
        tw = re.sub("%HYPHEN%", "-", tw)
        tw = re.sub("%TAG%", " #", tw)
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
        return tw["is_retweet"] or "Donald Trump" in tw["text"]

    def most_used_words(self):
        i = 0  # ranking of word frequency
        with open(self.path + "_vocab.txt", 'wb') as outfile:
            for key, value in sorted(self.dictionary.iteritems(), reverse=True, key=lambda (k, v): (v, k)):
                if value >= self.threshold:  # ignore words used less than four times
                    i += 1
                    outfile.write("{1}\n".format(i, key, value))  # ranking, word, num_use
                    self.vocab[key] = i  # basically a normalized, thresholded dictionary

    def generate_corpus(self):
        with open("{}_corpus.txt".format(self.path), 'wb') as out:
            for word in self.full_corpus.split(" "):
                if word != "":
                    try:
                        count = self.dictionary[word.lower()]
                        output = str(self.vocab[word.lower()]) + "\n" if count >= self.threshold else "0" + "\n"
                    except:
                        output = str(0) + "\n"  # this word has less than 4 occurrences
                    out.write(output)
        with open("{}_readable_corpus.txt".format(self.path), "wb") as f:
            f.write(str(self.full_corpus))

    def process_tweet(self):
        with open("{}.json".format(self.path), 'rb') as corpus:
            tweets = json.loads(corpus.read())
        for tweet in tweets:
            if self.useless(tweet):  # ignore third person
                continue
            words = self.clean(tweet["text"])
            self.add_to_dict(words)
            self.full_corpus.append(words)

    def generate(self, handle):  # creates other pieces of data
        self.path = "bot_files/{0}/{0}".format(handle)
        self.process_tweet()
        self.full_corpus = "".join(self.full_corpus)  # assemble into singe blob of text
        self.most_used_words()
        self.generate_corpus()


def generate_corpus(handle):
    """
    Generates the corpuses given a twitter handle
    :param handle: the handle of the account in question
    """
    print "generating corpus for %s..." % handle
    dat_boi = Tokenizer()
    dat_boi.generate(handle)
    print "done"

### visual analysis
# R commands
# input <- read.csv("/Users/matthew/Desktop/College/Junior/CS/CS540HW5/WARC201709/outfile.csv",header = TRUE)
# plot(c(1:dim(input)[1]),log(input[,1]),
#      xlab = "Word Rank", ylab = "Word Frequency", main = "Plot: Word Rank vs Frequency", col = "darkred")
# plot(c(1:dim(input)[1]),log(input[,1]),
#      xlab = "Word Rank", ylab = "Word Frequency (ln)", main = "Plot: Word Rank vs Frequency (ln)", col = "darkred")
