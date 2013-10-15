from collections import defaultdict

class BigramAnalyzer(object):
    def __init__(self, bigrams):
        self.formatted_bigrams = self._format_bigram(bigrams)

    def find_bigrams_for(self, word):
        return self.formatted_bigrams[word]

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

    def get_features(self, include_only=None, bigrams=[]):
        formatted_text = self.get_formatted_text()

        res = {}
        for word_i, word in enumerate(formatted_text):

            # Single features
            can_add = include_only == None or word in include_only
            if can_add:
                res['has(%s)' % word] = True

        return res
