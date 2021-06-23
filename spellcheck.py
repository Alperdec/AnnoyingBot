#Date 06/17/2021
#Author @Alper deCarion
#spellcheck v-1.0.3

# First model built upon BERT MLM, using a masked token to find likely candidates for the mispelled word

#      Second model iterated through the dictionary of valid english words and checked if edit distance < 3 
#  and added it to a dictionary where the least edited candidates were taken and evaluated for their respective probabilities of being the word in question
#  This was obviously slow and inefficient.

# This model instead builds off of Peter Norvig's as his idea to generate all possible strings 1 and 2 edit distances away AND THEN seeing if it is a known word is quite more efficient
# We will be adding two things: further edit distances, and computing the jaro_winkler_similarity as a final evaluation metric. (Levenshtein distances(1,2) -> P(word) -> Jaro-Winkler)
# 

import json
import nltk
import re
from nltk.corpus import gutenberg
from nltk.metrics.distance import jaro_winkler_similarity as jws
from collections import Counter

def get_text(text): 
    return re.findall(r'\w+', text.lower())

## building off of Peter Norvig's model, but making some upgrades @https://norvig.com/spell-correct.html
class SpellChecker:
    def __init__(self):
        self.counted_words = Counter(get_text((' '.join(gutenberg.words()))))
        self.N = len(self.counted_words)
        with open('words_dictionary.json', encoding='utf8') as f:
            self.words_dict = json.load(f)
        

    def __Relative_Liklihood(self, word):
        # returns the relative probability of a word
        # input: string
        # output: numerical value: n | 0 <= n < 1
        return (self.counted_words[word] / self.N)

    def __Relative_Liklihoods(self, words):
        # returns the relative probabilities of a set of words
        # input: set of words {w1, ..., wn}
        # output: dictionary {"word": P(word)}
        output_dict = {}
        for word in words:
            output_dict[word] = self.__Relative_Liklihood(word)
        return output_dict

    def __subset_of_known_words(self, words):
        # returns a subset of words that exist
        # input: set of strings
        # output: set of strings
        return set(word for word in words if word in self.words_dict)

    def __edit(self, word):
        # code stubbed from Peter Norvig
        letters    = 'abcdefghijklmnopqrstuvwxyz'
        splits     = [(word[:i], word[i:])    for i in range(len(word) + 1)]
        deletes    = [L + R[1:]               for L, R in splits if R]
        transposes = [L + R[1] + R[0] + R[2:] for L, R in splits if len(R)>1]
        replaces   = [L + c + R[1:]           for L, R in splits if R for c in letters]
        inserts    = [L + c + R               for L, R in splits for c in letters]
        return set(deletes + transposes + replaces + inserts)

    def __edit2(self, word):
        # generates words of 2 edit distances
        return (e_next for e_prev in self.__edit(word) for e_next in self.__edit(e_prev))

    def __edit3(self, word):
        # generates words of 3 edit distances
        # Makes program way slower to little known benefit (recommended to not use)
        return (e_next for e_prev in self.__edit2(word) for e_next in self.__edit(e_prev))

    def candidates(self, word):
        # gathers possible candidates of 1,2,3 edit distances, or the word exists, or return word
        output = set(self.__subset_of_known_words(self.__edit(word)))
        output.update(self.__subset_of_known_words(self.__edit2(word)))
        # add an ouput.update(known(edit3(word))) to experiment with 3 edit distances... however this was removed due to speed
        return (self.__subset_of_known_words([word]) or output or [word])

    def refined_candidates(self, word, candidates):
        # generates a dict of "word": jaro_winkler_similarity with val > 90%
        dist_dict = {}
        for candidate in candidates:
            val = jws(word, candidate)
            if len(candidate) < 5:
                if val > .84:
                    dist_dict[candidate] = val
            else:
                if val > .9:
                    dist_dict[candidate] = val
        return dist_dict       

    def select_most_probable(self, candidates):
        # selects the most probable word amongst candidates
        # jws Union commonality
        common_dict = self.__Relative_Liklihoods(candidates.keys())
        dist_dict = {}
        for item in candidates:
            if not item in common_dict:
                common_dict[item] = 0
            dist_dict[item] = candidates[item] + (100*common_dict[item])
        max_val = max(dist_dict.values())
        return [key for key in dist_dict if dist_dict[key] == max_val][0]

    def check_for_errors(self, sentence):
        possible_errors = {}
        normalized_sentence = sentence.lower()
        tokens = get_text(normalized_sentence)
        for token in tokens:
            print(token)
            if token in self.words_dict:
                continue
            candidates = self.candidates(token)
            candidates = self.refined_candidates(token, candidates)
            possible_errors[token] = self.select_most_probable(candidates)

        return possible_errors
