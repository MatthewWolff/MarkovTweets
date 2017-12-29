import json
import os
import random
import re
from datetime import datetime
from time import time

import colors

# constants
TWEET_MAX_LENGTH = 280


class Chain:
    def __init__(self, handle, max_chains, seed=None):
        random.seed(seed) if seed else random.seed()
        if max_chains < 1:
            raise ValueError("Chain length must be at least 1 (1 is not recommended tho)")
        self.seed = seed
        self.handle = handle
        self.chain_length = max_chains
        self.corpus, self.vocab = self.read_corpus_files()
        self.prob_distrib_one = self.survey_one_word()
        self.corpuses = self.analyze_corpus(max_chains)
        self.PERIOD = self.vocab.index(".")
        self.OOV = 0  # out of vocab

    def read_corpus_files(self):
        """
        Reads in the vocab and corpus
        :return: the requested files
        """
        with open("bot_files/{0}/{0}_corpus.txt".format(self.handle), 'rb') as infile:
            corpus = [int(line.strip()) for line in infile]
        with open("bot_files/{0}/{0}_vocab.txt".format(self.handle), 'rb') as infile:
            vocab = [line.strip() for line in infile]
        return corpus, vocab

    def generate_chain(self, max_length=TWEET_MAX_LENGTH):
        """
        Generates a series of sensibly-ordered words
        :return: A cleaned up series of sensibly-ordered words
        """

        def _len(o):
            return len(str(" ".join(map(self.get_word, o))))

        output = [self.get_acceptable_first_word()]
        while _len(output) < max_length:
            # try longest chain possible first
            hist_len = len(output[-(self.chain_length - 1):])
            history = " ".join(map(str, output[-hist_len:]))  # get history - if not enough, grabs what it can
            next_word = self.OOV
            while hist_len is not 0 and next_word is self.OOV:
                # print "Trying {}-chain w/history of {}".format(hist_len + 1, map(self.get_word, output[-hist_len:]))
                next_word = self.n_word(n=hist_len + 1, rand=random.random(), hist=history)
                hist_len -= 1  # try with highest chaining possible, then decrease
                history = " ".join(map(str, output[-hist_len:]))
                if next_word is self.OOV and hist_len is 0:  # don't stop trying until we have a usable word
                    while next_word is self.OOV:
                        next_word = self.one_word(random.random())
            output.append(next_word)
        try:
            clean = self.grammar(output, cutoff=max_length)
        except NoTerminalPuncException:
            return self.generate_chain()  # repeat until find a good enough chain #WARNING might be infinite lol
        return clean

    def get_word(self, index):
        """
        Given an index in the vocab, determines if valid and returns
        :param index: the word index that you're seeking
        :return: OOV if invalid, else the word you requested
        """
        return self.vocab[index - 1] if 0 < index < len(self.vocab) else "OOV"  # we treat 0's as Out Of Vocabulary

    def get_acceptable_first_word(self):
        """
        Not all words are acceptable for starting a sentence, so pick one that is
        :return: an acceptable first word
        """
        first_word = self.n_word(2, rand=random.random(), hist=self.PERIOD)  # pretend that the last "word" was period
        while self.get_word(first_word) in "?!.,OOV&/":  # list of "words" that we don't want as the first
            first_word = self.n_word(n=2, rand=random.random(), hist=self.PERIOD)
        return first_word

    def analyze_corpus(self, max_chains):
        """
        Analyzes the corpuses and generates a number of word locations to use for assessing probabilities
        :param max_chains: the maximum number of links in a chain the corpus needs to be able to generate
        :return: an array of arrays - each inner array holds key-value pairs, where the key is a history of words, and
            and the value is the index of the word that appears subsequently
        """
        # # NOTE: It seems more time efficient to just generate new chaining data, as bringing a 50-120MB file into
        # #     memory doesn't seem to be too quick in comparison
        # chain_data = "bot_files/{0}/{0}_markov_data.json".format(self.handle)
        # if self.check_markov_data():  # if good enough, load
        #     if os.path.exists(chain_data):
        #         print colors.yellow("retrieving chaining data...\n")
        #         with open(chain_data, "rb") as f:
        #             return json.load(f)

        print colors.yellow("analyzing corpus...")
        corpuses = [[]] * max_chains  # creates bodies of chain occurrences all at once
        corpuses[0] = self.survey_one_word()
        print colors.purple("\t1-chaining done")
        for n in range(1, max_chains):
            corpuses[n] = self.survey_n_words(n)
            print colors.purple("\t%s-chaining done" % (n + 1))
        print
        # print colors.yellow("\nstoring...\n")
        # with open(chain_data, 'wb') as outfile:
        #     json.dump(corpuses, outfile)
        return corpuses

    def survey_one_word(self):  # different than survey_n_words, as is independent from any history
        """
        Generates a list of probabilities to reference for selecting a word from the corpus
        :return: a list of probabilities that will sum to 1 when added up
        """
        prob_distrib = dict()
        for word in self.corpus:
            increment = 1 / float(len(self.corpus))
            if word in prob_distrib:
                prob_distrib[word] += increment
            else:
                prob_distrib[word] = increment
        return prob_distrib

    def survey_n_words(self, n):
        """
        Generates a dictionary of all possible histories and the words that occur immediately after
        :param n: the chain length that this corpus subset will help generate
        :return: the dictionary of histories and their subsequent words
        """
        offset = n - 1  # number of history words prior to the word
        hash_map = dict()
        for i in xrange(len(self.corpus)):
            if i < (len(self.corpus) - offset):  # if history words go up to the last word in corpus... what comes after
                next_ind = i + offset  # index of word after the history words... the word we'll reference later
                key = " ".join(map(str, self.corpus[i:i + n]))  # our history words
                # store
                if key in hash_map:
                    hash_map[key].append(next_ind)
                else:
                    hash_map[key] = [next_ind]
        return hash_map

    def one_word(self, rand):
        """
        Randomly grabs a word from the corpus
        :param rand: random float to use for grabbing a word
        :return: the random word index in vocab
        """
        total = i = 0
        for prob in self.prob_distrib_one.values():
            if total > rand:
                break
            total += prob
            i += 1
        return i - 1

    def n_word(self, n, rand, hist=None):
        """
        Generates the markov chain's n'th word's index in the vocab
        :param n: the length of the markov chain
        :param rand: a random float to use for selecting a word
        :param hist: the (n-1)-word history to work with
        :return: 0 if unable to find a word, otherwise an n'th word
        """
        if n is 1:
            return self.one_word(rand=rand)

        hist = str(hist)  # the string of ints gets parsed lol idk why
        if len(hist.split(" ")) is not n - 1:
            raise ValueError("Bad history given")

        hash_map = self.corpuses[n - 1]
        loci = hash_map[hist] if hist in hash_map else None
        if not loci:  # never occurs
            return 0
        prob_distrib = [0] * (len(self.vocab) + 1)
        for index in loci:
            if index < len(self.corpus) - 1:
                prob_distrib[self.corpus[index + 1]] += 1 / float(len(loci))
        total = i = 0
        for prob in prob_distrib:
            if total > rand:
                break
            total += prob
            i += 1
        return i - 1

    def grammar(self, output, cutoff):
        """
        Cleans up output for tweeting
        :param cutoff: Tweet is limited to this many characters
        :param output: the raw output to clean and format
        :return: return a cleaned up string for output
        """
        # make the tweet come to a logical end
        words_long = " ".join(map(self.get_word, output))  # readable output
        words = words_long[:cutoff]  # truncate
        while len(words) > 0 and (words[-1] not in "!?" and words[-3:] not in "..." and not self.is_real_period(words)):
            words = words[:-1]  # remove characters until it's a good ending point
        # clean up weird spacing
        clean = words
        clean = re.sub("(?<=[a-zA-Z0-9.]) (?=\.\.\.|[.,?!])|, ,|! [.,:]|, ?\.|& \.| (?='s)", "", clean)  # punctuation
        clean = re.sub("(?<=[.?!]) ([a-zA-Z])", lambda x: " " + x.group(1).upper(), clean)  # first letter after punct.
        clean = re.sub(" {2}", " ", clean)
        clean = re.sub(" i[,;!]? ", " I ", clean)  # uppercase I
        clean = re.sub("^([a-z])", lambda x: x.group(1).upper(), clean)  # first letter of tweet
        clean = re.sub("(?<=[. ])([a-z])(?=\.)", lambda x: x.group(1).upper(), clean)  # capitalize initialisms!
        # check mistakes
        if len(re.findall("OOV | OOV", clean)) is not 0:
            clean = re.sub("OOV | OOV", "", clean)
            print colors.red("removing OOV occurrences... :(")  # fuck
        if len(clean) is 0:
            raise NoTerminalPuncException("Could not terminate %s" % words_long)
        return clean

    @staticmethod
    def is_real_period(words):
        """
        Can't rely on any period to actually terminate a sentence, so this method will check if it does
        :param words: the entire tweet to check
        :return: True if the last character of the tweet is a terminal period
        """
        if words[-1] is not "." or words[-1] is " ":
            return False
        return len(re.findall("[. ][a-zA-Z]\.", words[-3:])) is 0  # checks that it's not part of an initialism

    def check_markov_data(self):
        """
        In order to keep track of the number of chains used to produce markove data (without reading in the entire
        file and checking the length of the object), we simply print a small file and then hide it.
        This method checks to see if the previous markov_data (if it exists) had the same number of chains
        :return: True if markov_data is acceptable, false if it needs to be regenerated
        """
        prev_markov = "bot_files/%s/.prev_markov" % self.handle
        good_enough = False
        if os.path.exists(prev_markov):
            prev_chain_length = open(prev_markov, "rb").read()
            good_enough = int(prev_chain_length) >= self.chain_length

        if not good_enough:
            with open(prev_markov, "wb") as outfile:
                outfile.write(str(self.chain_length) + "\n")
            os.system("chflags hidden {}".format(prev_markov))
        return good_enough


class NoTerminalPuncException(Exception):
    def __init__(self, *args):
        Exception.__init__(self, *args)
