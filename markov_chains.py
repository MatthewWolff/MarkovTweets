import random
from datetime import datetime
from time import time


def is_close(a, b, rel_tol=1e-09, abs_tol=0.0):
    return abs(a - b) <= max(rel_tol * max(abs(a), abs(b)), abs_tol)


class Chains:
    def __init__(self, handle, seed=int(datetime.now().strftime("%j"))):
        random.seed(seed)  # seeded by day in year unless otherwise specified
        self.corpus, self.vocab = self.read_corpus_files(handle)
        self.prob_distrib_one = self.survey_one_word()
        self.prob_distrib_two = self.survey_two_word()
        self.handle = handle

    @staticmethod
    def read_corpus_files(handle):
        with open("bot_files/{0}/{0}_corpus.txt".format(handle), 'rb') as infile:
            corpus = [int(line.strip()) for line in infile]
        with open("bot_files/{0}/{0}_vocab.txt".format(handle), 'rb') as infile:
            vocab = [line.strip() for line in infile]
        return corpus, vocab

    def generate_chain(self):
        output = []
        first_word = self.two_word(random.random(), 1)  # what word comes after the end of a sentence?
        output.append(first_word)
        hist = first_word
        while hist is not 12:
            rand = random.random()
            try:
                next = self.two_word(rand, hist)
            except:
                print "err:", rand, hist
                print "hehe i died, but here's what i made:"
                break
            output.append(next)
            hist = next
        print "@" + self.handle + " says: " + " ".join(map(self.get_word, output))

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
