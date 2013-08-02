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
from nltk.stem.porter import PorterStemmer
from nltk.corpus import stopwords

from redis import Redis

from urlparse import urlparse

N_TO_TEST = [10, 100, 1000, 10000, 15000]

POS_SENTENCES_PATH = 'rt-polarity-pos.txt'
NEG_SENTENCES_PATH = 'rt-polarity-neg.txt'
STOPWORDS = stopwords.words('english')
STEMMER = PorterStemmer()

QUOTE_RE = re.compile('(@\S+)\s')

def is_valid_url(url):
    import re
    regex = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return url is not None and regex.search(url)

def get_features():

    def _format(sentence, sentiment):

        sentence = QUOTE_RE.sub('', sentence)
        sentence = sentence.split()
        for w in sentence:
            if is_valid_url(w):
                sentence.remove(w)
        sentence = ' '.join(sentence)

        posWords = re.findall(r"[\w']+|[.,!?;]", sentence.rstrip())
        words = {}
        for word in posWords:
            #word = STEMMER.stem_word(word)
            word = word.lower()
            if word not in STOPWORDS:
                words[word] = True
        return words, sentiment


    client = Redis()

    pos_sentences = list(client.smembers('sentiment-analysis:positive'))
    neg_sentences = list(client.smembers('sentiment-analysis:negative'))

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

    score = nltk.classify.util.accuracy(classifier, map(_extract_valid, test_set))
    print 'Accuracy: ', score
    classifier.show_most_informative_features(10)

    return classifier, score

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
    #with futures.ProcessPoolExecutor(max_workers=2) as executor:
    res = {}
    for n in N_TO_TEST:
        # train a new classifier and then test accuracy
        print "Testing with %s high information features" % n
        print "-----------------------------------------"
        #executor.submit(evaluate_classifier, features[:n], pos_features, neg_features)
        classifier, score = evaluate_classifier(features[:n], pos_features, neg_features)
        res[score] = classifier
    
    # Get most accurate classifier
    classifier = res[max(res.keys())]
    print classifier



if __name__ == '__main__':
    main()
