import json
import os
import random
import re
from datetime import datetime
from time import time

import colors


class Chain:
    def __init__(self, handle, max_chains, seed=None, force_regen=False):
        random.seed(seed) if seed else random.seed()
        if max_chains < 1:
            raise ValueError("Chain length must be at least 1 (not recommended tho)")
        self.seed = seed
        self.handle = handle
        self.chain_length = max_chains
        self.corpus, self.vocab = self.read_corpus_files()
        self.prob_distrib_one = self.survey_one_word()
        self.corpuses = self.analyze_corpus(max_chains, force_regen=force_regen)
        self.PERIOD = self.vocab.index(".")
        self.OOV = 0

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

    def generate_chain(self):
        """
        Generates a series of sensibly-ordered words
        :return: A cleaned up series of sensibly-ordered words
        """
        output = [self.get_acceptable_first_word()]
        while output[-1] is not self.PERIOD and len(output) < 75:  # todo: more reasonable cutoff conditions
            # try longest chain possible first
            hist_len = len(output[-(self.chain_length - 1):])  # get history - if not enough, grabs what it can
            history = " ".join(map(str, output[-hist_len:]))
            next_word = self.OOV
            while hist_len is not 0 and next_word is self.OOV:
                # print "Trying {}-chain w/history of {}".format(hist_len + 1, map(self.get_word, output[-hist_len:]))
                next_word = self.n_word(n=hist_len + 1, rand=random.random(), hist=history)
                hist_len -= 1
                history = " ".join(map(str, output[-hist_len:]))
                if next_word is self.OOV and hist_len is 0:
                    while next_word is self.OOV:
                        next_word = self.one_word(random.random())
            output.append(next_word)
        clean = self.grammar(output)
        print colors.white("@" + self.handle) + colors.yellow(" says: ") + clean + "\n"
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
        Not all words are acceptable for starting a sentence
        :return: an acceptable word
        """
        first_word = self.n_word(2, rand=random.random(), hist=self.PERIOD)
        while self.get_word(first_word) in "?!.,OOV&/":
            first_word = self.n_word(n=2, rand=random.random(), hist=self.PERIOD)
        return first_word

    def analyze_corpus(self, max_chains, force_regen):
        """
        Decides whether the corpus needs to be analyzed/re-analyzed, and does so if needed
        :param max_chains: the maximum number of links in a chain the corpus needs to be able to generate
        :param force_regen: whether or not to force the corpus to regen (for instance, after you change the min
            word frequency of the corpus)
        :return:
        """
        chain_data = "bot_files/{0}/{0}_markov_data.json".format(self.handle)
        if self.check_markov_data() and not force_regen:  # if good enough, load
            if os.path.exists(chain_data):
                print colors.yellow("retrieving chaining data...\n")
                with open(chain_data) as f:
                    return json.load(f)

        print colors.yellow("analyzing corpus...") if not force_regen else colors.yellow("re-analyzing corpus...")
        corpuses = [[]] * max_chains  # creates bodies of chain occurrences all at once
        corpuses[0] = self.survey_one_word()
        print colors.purple("\t1-chaining done")
        for n in range(1, max_chains):
            offset = n - 1
            hash_map = dict()
            for i, word in enumerate(self.corpus):
                if i < (len(self.corpus) - offset):
                    next_ind = i + offset
                    key = " ".join(map(str, self.corpus[i:i + n]))
                    if key in hash_map:
                        hash_map[key].append(next_ind)
                    else:
                        hash_map[key] = [next_ind]
            corpuses[n] = hash_map
            print colors.purple("\t{}-chaining done".format(n + 1))
        print colors.yellow("\nstoring...\n")
        with open(chain_data, 'wb') as outfile:
            json.dump(corpuses, outfile)
        return corpuses

    def survey_one_word(self):
        """
        generates a list of probabilities to reference for selecting a word from the corpus
        :return:
        """
        prob_distrib = dict()
        for word in self.corpus:
            increment = 1 / float(len(self.corpus))
            if word in prob_distrib:
                prob_distrib[word] += increment
            else:
                prob_distrib[word] = increment
        return prob_distrib

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
            raise Exception("Bad history given")

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

    def grammar(self, output):
        """
        Cleans up output for tweeting
        :param output: the raw output to clean and format
        :return: return a cleaned up string for output
        """
        clean = " ".join(map(self.get_word, output))  # readable output
        clean = re.sub("(?<=[a-zA-Z0-9.]) (?=\.\.\.|[.,?!])|OOV | OOV|, ,|, ?\.|& \.| (?='s)", "", clean)  # punctuation
        clean = re.sub("(?<=[.?!]) ([a-zA-Z])", lambda x: " " + x.group(1).upper(), clean)  # first letter after punct.
        clean = re.sub(" {2}", " ", clean)
        clean = re.sub(" i[,;!]? ", " I ", clean)  # uppercase I
        clean = re.sub("^([a-z])", lambda x: x.group(1).upper(), clean)  # first letter of tweet
        clean = re.sub("(?<=[. ])([a-z])(?=\.)", lambda x: x.group(1).upper(), clean)
        clean = clean
        return clean

    def check_markov_data(self):
        """
        Checks to see if the previous markov_data (if it exists) had the same number of chains)
        :return: Whether True if markov_data is acceptable, false if it needs to be regenerated
        """
        prev_markov = "bot_files/{0}/.prev_markov".format(self.handle)
        good_enough = False
        if os.path.exists(prev_markov):
            prev_chain_length = open(prev_markov, "rb").read()
            good_enough = int(prev_chain_length) >= self.chain_length

        if not good_enough:
            with open(prev_markov, "wb") as outfile:
                outfile.write(str(self.chain_length) + "\n")
            os.system("chflags hidden {}".format(prev_markov))
        return good_enough
