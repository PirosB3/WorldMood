import os
import pickle

from collections import defaultdict

from nltk.classify import NaiveBayesClassifier
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
    def __init__(self, phrases, formatter):
        self.phrases = phrases
        self.formatter = formatter

    def _get_class_sentiments(self):
        return self.phrases.keys()

    def get_bigram_analyzer(self, n):
        words = []
        for sentiment in self._get_class_sentiments():
            formatted_words_in_phrases = [p.get_formatted_text(self.formatter)
                for p in self.phrases[sentiment]]
            print "Passing word for bigram analyzer: %s" % formatted_words_in_phrases
            for word in formatted_words_in_phrases:
                words.extend(word)

        bigram_measures = collocations.BigramAssocMeasures()
        finder = collocations.BigramCollocationFinder.from_words(words)
        return BigramAnalyzer(finder.nbest(bigram_measures.likelihood_ratio, n))

    def iterate_phrases(self):
        for sentiment in self._get_class_sentiments():
            for phrase in self.phrases[sentiment]:
                yield sentiment, phrase

    def _build_prob_dist(self, fd, cfd):
        for sentiment, phrase in self.iterate_phrases():
            formatted_text = phrase.get_formatted_text(self.formatter)
            print "Passing word for prob dist: %s" % formatted_text
            for word in formatted_text:
                fd.inc(word)
                cfd[sentiment].inc(word)
        return fd, cfd

    def get_most_informative_features(self, min_score):
        freq_dist, cond_freq_dist = self._build_prob_dist(FreqDist(),
            ConditionalFreqDist())
        res = []
        for word, total_freq in freq_dist.iteritems():
            score = 0
            for sentiment in self._get_class_sentiments():
                score += BigramAssocMeasures.chi_sq(
                    cond_freq_dist[sentiment][word],
                    (total_freq, cond_freq_dist[sentiment].N()),
                    freq_dist.N()
                )
            res.append((score, word))
        
        order_res = sorted(res, reverse=True)
        result_res = []
        for score, word in order_res:
            if score >= min_score:
                result_res.append(word)
            else:
                break
        return result_res

    def train_classifier(self, formatter, n_bigrams, min_score_features):
        feats = self.get_most_informative_features(min_score_features)
        bigrams = self.get_bigram_analyzer(n_bigrams)

        return TrainedClassifier(formatter, bigrams, feats, phrases_map=self.phrases)

class TrainedClassifier(object):
    CLASSIFIER_CONSTRUCTOR = NaiveBayesClassifier

    @staticmethod
    def load(s_dir, formatter):
        with open(os.path.join(s_dir, 'classifier.pickle'), 'r') as classifier:
            with open(os.path.join(s_dir, 'bigrams.pickle'), 'r') as bigrams:
                with open(os.path.join(s_dir, 'feats.pickle'), 'r') as feats:
                    classifier = pickle.loads(classifier.read())
                    feats = pickle.loads(feats.read())
                    bigrams = pickle.loads(bigrams.read())
                    return TrainedClassifier(formatter, bigrams, feats,
                        classifier= classifier)

    def __init__(self, formatter, bigrams, feats, phrases_map = None, classifier= None):
        self.formatter = formatter
        self.bigrams = bigrams
        self.feats = feats

        if phrases_map:
            training_set = []
            for sentiment, phrases in phrases_map.iteritems():
                for p in phrases:
                    vec = self._phrase_to_feature_vector(p)
                    print "Passing word for feature vector composition: %s" % vec
                    if vec:
                        training_set.append((vec, sentiment))

            self.classifier = self.CLASSIFIER_CONSTRUCTOR.train(training_set)
        elif classifier:
            self.classifier = classifier
        else:
            raise Exception("No classifier provided")

    def get_components(self):
        return self.bigrams, self.feats

    def _phrase_to_feature_vector(self, phrase):
        res = phrase.get_features(self.formatter, self.feats, self.bigrams)
        if len(res.keys()) < 1:
            return None
        return res

    def batch_classify(self, phrases):
        return map(self.classify, phrases)

    def classify(self, phrase):
        feature_vector = phrase.get_features(self.formatter, self.feats,
            self.bigrams)
        if feature_vector:
            return self.classifier.classify(feature_vector)
        return None

    def prob_classify(self, phrase):
        feature_vector = phrase.get_features(self.formatter, self.feats,
            self.bigrams)
        if feature_vector:
            return self.classifier.prob_classify(feature_vector)
        return None

    def serialize(self, s_dir, serializer=pickle, write_function=open):
        to_write = {
            os.path.join(s_dir, 'classifier.pickle'): self.classifier,
            os.path.join(s_dir, 'bigrams.pickle'): self.bigrams,
            os.path.join(s_dir, 'feats.pickle'): self.feats
        }
        for path, obj in to_write.iteritems():
            with write_function(path, 'w') as f:
                serializer.dump(obj, f)
