#!/usr/bin/python2.7
import json
import re


class Tokenizer:
    def __init__(self):
        self.dictionary = dict()
        self.full_corpus = []
        self.path = ""

    @staticmethod
    def clean(text):
        tw = text
        tw = re.sub("(https?://.*)|(www\..*)|(t\.co.*)|(amzn\.to.*)( |$)", "", tw)  # remove links
        tw = re.sub("RE:", "", tw)
        tw = re.sub("Donald J\. Trump", "", tw)
        tw = re.sub("#", "%TAG%", tw)  # hashtagging
        tw = re.sub("@|\.@", "%AT%", tw)  # @
        tw = re.sub("\.\.+", "%ELLIPSE%", tw)  # ellipses
        tw = re.sub("&amp;", "%AMPERSAND%", tw)
        tw = re.sub("(?<=[a-zA-Z])-(?=[a-zA-Z])", "%HYPHEN%", tw)
        tw = re.sub("(?<=[a-zA-Z])\.( |$)", " . ", tw)  # punctuation
        tw = re.sub("!+", " ! ", tw)
        tw = re.sub("(?<=[^0-9])?,(?=[^0-9])", " , ", tw)
        tw = re.sub("\?+", " ? ", tw)
        tw = re.sub("--|-|[()<>]", " ", tw)
        tw = re.sub("\(cont\)", "", tw)
        tw = re.sub("[^a-zA-Z0-9,?!%&' .]", "", tw)  # remove pretty much everything, including emoji
        tw = re.sub("%AT%", "@", tw)
        tw = re.sub("%ELLIPSE% ?", " ... ", tw)
        tw = re.sub(" ?%AMPERSAND% ?", " & ", tw)
        tw = re.sub("%HYPHEN%", "-", tw)
        tw = re.sub("%TAG%", " #", tw)
        last = tw[-5:].strip()  # check to see if we need to add a period
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
        x_list = []
        y_list = []
        for key, value in sorted(self.dictionary.iteritems(), reverse=True, key=lambda (k, v): (v, k)):
            i += 1
            x_list.append(i)
            y_list.append(value)
            if value > 3:  # ignore words used less than four times
                print "%d - %s: %s" % (i, key, value)

    def generate_corpus(self):
        out_num = open("{}_num_corpus.txt".format(self.path), 'wb')
        out_word = open("{}_word_corpus.txt".format(self.path), 'wb')
        for word in self.full_corpus.split(" "):
            if word != "":
                try:
                    count = self.dictionary[word.lower()]
                    output = str(count) + "\n" if count >= 4 else "0" + "\n"

                except:
                    output = str(0) + "\n"  # this word has less than 4 occurrences
                out_num.write(output)
                out_word.write(word + "\n")
        out_num.close()
        out_word.close()
        with open("{}_readable_corpus.txt".format(self.path), "wb") as f:
            f.write(str(self.full_corpus))

    def generate(self, handle):
        self.path = "bot_files/{0}/{0}".format(handle)
        with open("{}.json".format(self.path), 'rb') as corpus:
            tweets = json.loads(corpus.read())
        for tweet in tweets:
            if self.useless(tweet):  # ignore third person
                continue
            words = self.clean(tweet["text"])
            self.add_to_dict(words)
            self.full_corpus.append(words)

        self.full_corpus = "".join(self.full_corpus)  # assemble into singe blob of text
        self.generate_corpus()


def generate(handle):
    """
    Generates the corpuses given a twitter handle
    :param handle: the handle of the account in question
    """
    print "generating corpus for %s..." % handle
    dat_boi = Tokenizer()
    dat_boi.generate(handle)
    print "done"


if __name__ == "__main__":
    generate("joshlukas97")
### visual analysis
# R commands
# input <- read.csv("/Users/matthew/Desktop/College/Junior/CS/CS540HW5/WARC201709/outfile.csv",header = TRUE)
# plot(c(1:dim(input)[1]),log(input[,1]),
#      xlab = "Word Rank", ylab = "Word Frequency", main = "Plot: Word Rank vs Frequency", col = "darkred")
# plot(c(1:dim(input)[1]),log(input[,1]),
#      xlab = "Word Rank", ylab = "Word Frequency (ln)", main = "Plot: Word Rank vs Frequency (ln)", col = "darkred")
