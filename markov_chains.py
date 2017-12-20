import random
import re
from datetime import datetime
from time import time


def is_close(a, b, rel_tol=1e-09, abs_tol=0.0):
    return abs(a - b) <= max(rel_tol * max(abs(a), abs(b)), abs_tol)


class Chain:
    def __init__(self, handle, max_chains=3, seed=int(datetime.now().strftime("%s"))):
        random.seed(seed)  # seeded by day in year unless otherwise specified
        self.corpus, self.vocab = self.read_corpus_files(handle)
        self.prob_distrib_one = self.survey_one_word()
        self.prob_distrib_two = self.survey_two_word()
        self.corpuses = self.analyze_corpus(max_chains)
        self.chain_length = max_chains
        self.handle = handle
        self.PERIOD = self.vocab.index(".")
        self.OOV = 0

    @staticmethod
    def read_corpus_files(handle):
        with open("bot_files/{0}/{0}_corpus.txt".format(handle), 'rb') as infile:
            corpus = [int(line.strip()) for line in infile]
        with open("bot_files/{0}/{0}_vocab.txt".format(handle), 'rb') as infile:
            vocab = [line.strip() for line in infile]
        return corpus, vocab

    def generate_chain(self):
        print "Beginning chain generation..."
        output = []
        # get first word
        first_word = self.two_word(random.random(), self.vocab.index("."))  # whatever comes after a period lol
        while first_word is self.OOV or first_word is self.PERIOD or first_word is self.vocab.index(","):
            first_word = self.one_word(random.random())  # sometimes it's whiny idk TODO delete

        output.append(first_word)
        while output[-1] is not self.PERIOD and len(output) < 100:
            rand = random.random()
            # try:
            # try longest chain possible first
            hist_len = len(output[-(self.chain_length - 1):])  # get history - if not enough, grabs what it can
            history = " ".join(map(str, output[-hist_len:]))
            next_word = self.OOV
            while hist_len is not 0 and next_word is self.OOV:
                # print "Attempting {}-chain with a history of {}".format(hist_len + 1,
                #                                                         map(self.get_word, output[-hist_len:]))
                next_word = self.n_word(n=hist_len + 1, rand=rand, hist=history)
                hist_len -= 1
                history = " ".join(map(str, output[-hist_len:]))
                rand = random.random()
                if next_word is self.OOV and hist_len is 0:
                    while next_word is self.OOV:
                        next_word = self.one_word(random.random())
            output.append(next_word)
        clean = self.grammar(output)
        print clean
        return clean

    def get_word(self, index):
        return self.vocab[index - 1] if 0 < index < len(self.vocab) else "OOV"  # we treat 0's as Out Of Vocabulary

    def survey_one_word(self):
        prob_distrib = dict()
        for word in self.corpus:
            increment = 1 / float(len(self.corpus))
            if word in prob_distrib:
                prob_distrib[word] += increment
            else:
                prob_distrib[word] = increment
        return prob_distrib

    def analyze_corpus(self, max_chains):
        # TODO save the chaining, mainly bc once the chains get long enough it'll be a pain
        print "analyzing corpus..."
        corpuses = [[]] * max_chains  # creates bodies of chain occurrences all at once
        corpuses[0] = self.survey_one_word()
        print "\t1-chaining done"
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
            print "\t%i-chaining done" % (n + 1)
        print
        return corpuses

    def n_word(self, n, rand, hist=""):
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

    def one_word(self, rand):
        total = i = 0
        for prob in self.prob_distrib_one.values():
            if total > rand:
                break
            total += prob
            i += 1
        return i - 1

    def survey_two_word(self):
        hash_map = dict()
        for i, word in enumerate(self.corpus):
            word = str(word)
            if word in hash_map:
                hash_map[word].append(i)
            else:
                hash_map[word] = [i]
        return hash_map

    def two_word(self, rand, hist):
        loci = self.prob_distrib_two[hist] if hist in self.prob_distrib_two else None
        if not loci:  # premature termination, user (AKA i) probably fucked up
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
        raw = "\n@" + self.handle + " says: " + " ".join(map(self.get_word, output))
        raw = re.sub("(?<=[a-zA-Z0-9]) (?=\.\.\.|[.,?!])", "", raw)  # punctuation
        raw = re.sub("(?<=[.?!]) ([a-zA-Z])", lambda x: " " + x.group(1).upper(), raw)  # all other letters
        return re.sub("(?<=says: )([a-z])", lambda x: x.group(1).upper(), raw)  # first letter of sentence
