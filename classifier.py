import futures
import functools
import heapq
import os
from collections import defaultdict
import re, math, collections, itertools
import nltk, nltk.classify.util, nltk.metrics
from nltk.classify import NaiveBayesClassifier
from nltk.metrics import BigramAssocMeasures
from nltk.probability import FreqDist, ConditionalFreqDist
from nltk.corpus import stopwords

N_TO_TEST = [10, 100, 1000, 10000]

POS_SENTENCES_PATH = 'rt-polarity-pos.txt'
NEG_SENTENCES_PATH = 'rt-polarity-neg.txt'
STOPWORDS = stopwords.words('english')

def get_features():

    def _format(sentence, sentiment):
        posWords = re.findall(r"[\w']+|[.,!?;]", sentence.rstrip())
        words = {}
        for word in posWords:
            if word not in STOPWORDS:
                words[word] = True
        return words, sentiment


    with open(POS_SENTENCES_PATH, 'r') as pos_file:
        with open(NEG_SENTENCES_PATH, 'r') as neg_file:
            pos_sentences = re.split(r'\n', pos_file.read())
            neg_sentences = re.split(r'\n', neg_file.read())

            pos_features = map(functools.partial(_format, sentiment='pos'), pos_sentences)
            neg_features = map(functools.partial(_format, sentiment='neg'), neg_sentences)
            return pos_features, neg_features

def get_most_informative_features(freq_dist, cond_freq_dist):
    pos_word_count = cond_freq_dist['pos'].N()
    neg_word_count = cond_freq_dist['neg'].N()
    total_word_count = pos_word_count + neg_word_count

    result = []
    for word, total_freq in freq_dist.iteritems():
        pos_score = BigramAssocMeasures.chi_sq(cond_freq_dist['pos'][word], (
            total_freq, pos_word_count), total_word_count)
        neg_score = BigramAssocMeasures.chi_sq(cond_freq_dist['neg'][word], (
            total_freq, neg_word_count), total_word_count)
        result.append((pos_score + neg_score, word))
    return [word for score, word in sorted(result, reverse=True)]

def evaluate_classifier(valid_features, pos_features, neg_features):

    def _extract_valid(feature):
        res = {}
        keys, sentiment = feature
        for key in keys.keys():
            if key in valid_features:
                res[key] = True
        return (res, sentiment)

    pos_cutoff = len(pos_features) * 3/4
    neg_cutoff = len(neg_features) * 3/4
    train_set = pos_features[:pos_cutoff] + neg_features[:neg_cutoff]
    test_set = pos_features[pos_cutoff:] + neg_features[neg_cutoff:]

    classifier = NaiveBayesClassifier.train(map(_extract_valid, train_set))
    print "Built classifier."

    print 'Accuracy: ', nltk.classify.util.accuracy(classifier, map(_extract_valid, test_set))
    classifier.show_most_informative_features(10)

def main():
    # Fetch features from phrases
    pos_features, neg_features = get_features()

    # create frequency distribution
    freq_dist = FreqDist()
    cond_freq_dist = ConditionalFreqDist()
    for features, sentiment in [(pos_features, 'pos'), (neg_features, 'neg')]:
        for feature in features:
            for word in feature[0].keys():
                freq_dist.inc(word)
                cond_freq_dist[sentiment].inc(word)

    # Get most informative features
    features = get_most_informative_features(freq_dist, cond_freq_dist)
    with futures.ProcessPoolExecutor(max_workers=2) as executor:
        for n in N_TO_TEST:
            # train a new classifier and then test accuracy
            print "Testing with %s high information features" % n
            print "-----------------------------------------"
            executor.submit(evaluate_classifier, features[:n], pos_features, neg_features)



if __name__ == '__main__':
    main()
