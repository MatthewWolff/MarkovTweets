import random
from datetime import datetime
from time import time


class Chains:
    def __init__(self, handle, seed=random.seed(int(datetime.now().strftime("%j")))):
        self.seed = seed  # seeded by day in year unless otherwise specified
        self.corpus, self.vocab = self.read_corpus_files(handle)
        self.prob_distrib_one = self.survey_one_word()

    @staticmethod
    def read_corpus_files(handle):
        with open("bot_files/{0}/{0}_corpus.txt".format(handle), 'rb') as infile:
            corpus = [int(line.strip()) for line in infile]
        with open("bot_files/{0}/{0}_vocab.txt".format(handle), 'rb') as infile:
            vocab = [line.strip() for line in infile]
        return corpus, vocab

    def generate_chain(self):
        pass

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
        for prob in self.prob_distrib_one:
            if total > rand:
                break
            total += prob
            i += 1
        return i - 1

    def survey_two_word(self):
        prob_distrib = dict()
        itr = iter(self.corpus)
        while itr is not None:
            itr = next(itr)
            itr

# 	private static Map<Integer, List<Integer>> survey_two_word(){
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
