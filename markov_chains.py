import random
import sys
from datetime import datetime
from time import time


def is_close(a, b, rel_tol=1e-09, abs_tol=0.0):
    return abs(a - b) <= max(rel_tol * max(abs(a), abs(b)), abs_tol)


class Chains:
    def __init__(self, handle, max_chains=3, seed=int(datetime.now().strftime("%j"))):
        random.seed(seed)  # seeded by day in year unless otherwise specified
        self.corpus, self.vocab = self.read_corpus_files(handle)
        self.prob_distrib_one = self.survey_one_word()
        self.prob_distrib_two = self.survey_two_word()
        self.corpuses = self.analyze_corpus(max_chains)
        self.chain_length = max_chains
        self.handle = handle

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
        first_word = self.two_word(random.random(),
                                   self.vocab.index("."))  # whatever likely comes after a period lol
        while first_word is 0 or first_word is 1:  # can't be OOV or .
            first_word = self.one_word(random.random())  # sometimes it's whiny idk TODO delete

        output.append(first_word)
        hist_len = -1  # declare
        while output[-1] is not 1 and len(output) < 100:
            rand = random.random()
            try:
                # try longest chain possible
                hist_len = len(output[-(self.chain_length - 1):])  # get history - if not enough, grabs what it can
                history = " ".join(map(str, output[-hist_len:]))
                next_word = 0
                while hist_len is not 0 and next_word is 0:
                    next_word = self.n_word(n=hist_len + 1, rand=rand, hist=history)
                    hist_len -= 1
                    history = " ".join(map(str, output[-hist_len:]))
                    rand = random.random()
                    if next_word is 0 and hist_len is 0:
                        while next_word is 0:
                            next_word = self.one_word(random.random())

            except Exception as e:
                print "\nerr {}:\nrand was {}".format(e, rand)
                print "hehe i died, but here's what i made:"
                break

            # print "produced {} at {}-chain".format(self.get_word(next_word), len(history.split(" ")) + 1)
            output.append(next_word)
        print "\n@" + self.handle + " says: " + " ".join(map(self.get_word, output))

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
        # TODO testing - delete
        # print i-1
        # print total - self.prob_distrib_one[i-1]
        # print total
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
        # TODO testing - delete
        # if is_close(0, rand):
        #     print "%i\n%f\n%f\n" % (i - 1, 0, total)
        # else:
        #     print "%i\n%f\n%f\n" % (i - 1, total - self.prob_distrib_one[i - 1], total)
        # for x in prob_distrib:
        #     if not is_close(0, x):
        #         print x
        return i - 1

# # # Code from my java chatbot
#   private static Map<Integer, List<Integer>> survey_two_word(){
# 		Map<Integer, List<Integer>> map = new HashMap<Integer, List<Integer>>(4700);
# 		ListIterator<Integer> it = corpus.listIterator();
# 		while(it.hasNext()) {
# 			int i = it.nextIndex(), word = it.next(); // better than retrieving word from index each time
# 			if(map.containsKey(word))
# 				map.get(word).add(i); // create list of all occurrences of each word
# 			else
# 				map.put((Integer) word, new ArrayList<Integer>(Arrays.asList((Integer) i)));
# 		}
# 		return map;
# 	}
# 	private static Map<String, List<Integer>> survey_three_word(){
# 		Map<String, List<Integer>> map = new HashMap<String, List<Integer>>(4700);
# 		ListIterator<Integer> it = corpus.listIterator();
# 		while(it.hasNext() && it.nextIndex() < corpus.size()-1)
# 		{
# 			int word1 = it.next(), word2 = slick_corpus[it.nextIndex()];
# 			if(map.containsKey(word1 + " " + word2)) // new key format
# 				map.get(word1 + " " + word2).add(it.nextIndex()); // create list of all occurrences of each word pair
# 			else
# 				map.put(word1 + " " + word2, new ArrayList<Integer>(Arrays.asList((Integer) it.nextIndex())));
# 		}
# 		return map;
# 	}
# 	private static int two_word(Map<Integer, List<Integer>> map, double rand, int h){
# 		// count up
# 		Double[] prob_distrib = new Double[4700]; Arrays.fill(prob_distrib, 0.0);
# 		List<Integer> loci = map.containsKey(h) ? map.get(h) : null;
# 		if(loci != null)
# 			for(int index : loci) // list of all h's
# 				if(index < corpus.size()) // if the word after is w, increment
# 					prob_distrib[slick_corpus[index+1]] += 1/(double)loci.size();
#
# 		// calculate
# 		double sum = 0; int i;
# 		for(i = 0; i < prob_distrib.length && sum <= rand; i++)
# 			sum += prob_distrib[i];
# 		return --i;
# 	}
# 	private static int three_word(Map<String, List<Integer>> map, double rand, int h1, int h2){
# 		// count up
# 		Double[] prob_distrib = new Double[4700]; Arrays.fill(prob_distrib, 0.0);
# 		List<Integer> loci = map.containsKey(h1 + " " + h2) ? map.get(h1 + " " + h2) : null;
# 		if(loci != null)
# 			for(int index : loci) // list of all h's
# 				if(index < corpus.size()) // if the word after is w, increment
# 					prob_distrib[slick_corpus[index+1]] += 1/(double)loci.size();
#
# 		// calculate
# 		double sum = 0; int i;
# 		for(i = 0; i < prob_distrib.length && sum <= rand; i++)
# 			sum += prob_distrib[i];
# 		return --i;
# 	}
# }
