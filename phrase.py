from collections import defaultdict

class BigramAnalyzer(object):
    def __init__(self, bigrams):
        self.formatted_bigrams = self._format_bigram(bigrams)

    def find_bigrams_for(self, word):
        return self.formatted_bigrams[word]

    def scan_features_for_bigrams(self, features):
        res = []
        for i, word in enumerate(features):
            bg = self.find_bigrams_for(word)
            if bg:
                try:
                    next_word = features[i+1]
                    if next_word in bg:
                        res.append((word, next_word))
                except IndexError:
                    return res
        return res

    def _format_bigram(self, bigrams):
        res = defaultdict(list)
        for term1, term2 in bigrams:
            res[term1].append(term2)
        return res

class Phrase(object):
    def __init__(self, text, formatter):
        self.text = text
        self.formatter = formatter

    def get_text(self):
        return self.text

    def get_formatted_text(self):
        return self.formatter.process(self.text)

    def get_features(self, include_only=None, bigram_analyzer=None):
        formatted_text = self.get_formatted_text()

        res = {}
        for word_i, word in enumerate(formatted_text):

            # Single features
            can_add = include_only == None or word in include_only
            if can_add:
                res['has(%s)' % word] = True

        if bigram_analyzer:
            bigrams = bigram_analyzer.scan_features_for_bigrams(formatted_text)
            for terma, termb in bigrams:
                res['has(%s,%s)' % (terma, termb)] = True

        return res
