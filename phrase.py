from collections import defaultdict

from nltk.metrics import BigramAssocMeasures
from nltk.probability import FreqDist, ConditionalFreqDist
from nltk import collocations

class Word(object):
    def __init__(self, word):
        self.word = word

    def get_word(self):
        return self.word

    def get_formatted_word(self, formatter):
        return formatter.process_word(self.word)

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
    def __init__(self, text, tokenizer):
        self.tokenizer = tokenizer
        self.words = [Word(w) for w in tokenizer(text)]

    def get_text(self):
        return ' '.join([w.get_word() for w in self.words])

    def get_formatted_text(self, formatter):
        return filter(None, [w.get_formatted_word(formatter)
            for w in self.words])

    def get_features(self, formatter, n_features=None, bigram_analyzer=None):
        formatted_text = self.get_formatted_text(formatter)

        res = {}
        for word_i, word in enumerate(formatted_text):

            # Single features
            can_add = n_features == None or word in n_features
            if can_add:
                res['has(%s)' % word] = True

        if bigram_analyzer:
            bigrams = bigram_analyzer.scan_features_for_bigrams(formatted_text)
            for terma, termb in bigrams:
                res['has(%s,%s)' % (terma, termb)] = True

        return res

class TextProcessor(object):
    def __init__(self, phrases):
        self.phrases = phrases

    def _get_class_sentiments(self):
        return self.phrases.keys()

    def get_bigrams(self, n):
        words = []
        for sentiment in self._get_class_sentiments():
            word_features = [p.get_formatted_text() for p in self.phrases[sentiment]]
            words.update(word_features)

        bigram_measures = collocations.BigramAssocMeasures()
        finder = collocations.BigramCollocationFinder.from_words(words)
        return finder.nbest(bigram_measures.pmi, n)

    def _build_prob_dist(self, fd, cfd):
        sentiments = self.phrases.keys()
        for sentiment in sentiments:
            for phrase in self.phrases[sentiment]:
                formatted_text = phrase.get_formatted_text()
                for word in formatted_text:
                    fd.inc(word)
                    cfd[sentiment].inc(word)
        return fd, cfd

    def get_most_informative_features(self, n):
        freq_dist, cond_freq_dist = self._build_prob_dist(FreqDist(),
                                        ConditionalFreqDist())
        res = []
        for word, total_freq in freq_dist.iteritems():
            score = 0
            for sentiment in self._get_class_sentiments():
                score += BigramAssocMeasures.chi_sq(
                    cond_freq_dist[sentiment][word],
                    (total_freq, cond_freq_dist[sentiment].N()),
                    total_word_count
                )
            res.append((score, word))
        return [word for score, word in sorted(res, reverse=True)][:n]
