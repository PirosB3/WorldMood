import zmq
import redis
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
from formatting import FormatterPipeline
import formatting

N_TO_TEST = [500, 800, 900, 1000, 1150]
RT_RE = re.compile('@[A-Za-z0-9]+')
HASHTAG_RE = re.compile('#\w*[a-zA-Z_]+\w*')

FORMATTER = FormatterPipeline(
    formatting.make_lowercase,
    formatting.strip_urls,
    formatting.strip_hashtags,
    formatting.strip_names,
    formatting.replace_html_entities,
    formatting.remove_repetitons,
    functools.partial(
        formatting.remove_noise,
        stopwords = stopwords.words('english') + ['rt']
    ),
    functools.partial(
        formatting.stem_words,
        stemmer= nltk.stem.porter.PorterStemmer()
    ),
    functools.partial(
        formatting.lemmatize_words,
        lemmatizer= nltk.stem.wordnet.WordNetLemmatizer()
    )
)

def get_features():

    def _format(sentence, sentiment):
        formatted_sentence = FORMATTER.process(sentence)
        #print formatted_sentence

        x = {}
        for z in nltk.wordpunct_tokenize(formatted_sentence):
            x[z] = True
        return x, sentiment


    client = redis.Redis()
    pos_sentences = list(client.smembers('sentiment-analysis-4:positive'))
    neg_sentences = list(client.smembers('sentiment-analysis-4:negative'))
    neutral_sentences = list(client.smembers('sentiment-analysis-4:neutral'))

    pos_features = map(functools.partial(_format, sentiment='pos'), pos_sentences)
    neg_features = map(functools.partial(_format, sentiment='neg'), neg_sentences)
    neutral_features = map(functools.partial(_format, sentiment='neutral'), neutral_sentences)
    return pos_features, neg_features, neutral_features

def get_most_informative_features(freq_dist, cond_freq_dist):
    pos_word_count = cond_freq_dist['pos'].N()
    neg_word_count = cond_freq_dist['neg'].N()
    neutral_word_count = cond_freq_dist['neutral'].N()
    total_word_count = pos_word_count + neg_word_count + neutral_word_count

    result = []
    for word, total_freq in freq_dist.iteritems():
        pos_score = BigramAssocMeasures.chi_sq(cond_freq_dist['pos'][word], (
            total_freq, pos_word_count), total_word_count)
        neg_score = BigramAssocMeasures.chi_sq(cond_freq_dist['neg'][word], (
            total_freq, neg_word_count), total_word_count)
        neutral_score = BigramAssocMeasures.chi_sq(cond_freq_dist['neutral'][word], (
            total_freq, neg_word_count), total_word_count)
        result.append((pos_score + neg_score + neutral_score, word))
    return [word for score, word in sorted(result, reverse=True)]

def evaluate_classifier(valid_features, pos_features, neg_features, neutral_features):

    def _extract_valid(feature):
        res = {}
        keys, sentiment = feature
        for key in keys.keys():
            if key in valid_features:
                res[key] = True
        return (res, sentiment)

    pos_cutoff = len(pos_features) * 3/4
    neg_cutoff = len(neg_features) * 3/4
    neutral_cutoff = len(neutral_features) * 3/4
    train_set = pos_features[:pos_cutoff] + neg_features[:neg_cutoff] + neutral_features[:neutral_cutoff]
    test_set = pos_features[pos_cutoff:] + neg_features[neg_cutoff:] + neutral_features[neutral_cutoff:]

    classifier = NaiveBayesClassifier.train(map(_extract_valid, train_set))
    print "Built classifier."

    classifier.show_most_informative_features(10)
    accuracy = nltk.classify.util.accuracy(classifier, map(_extract_valid, test_set))
    print 'Accuracy: ', accuracy
    return accuracy, classifier

def main():
    # Fetch features from phrases
    pos_features, neg_features, neutral_features = get_features()

    # create frequency distribution
    freq_dist = FreqDist()
    cond_freq_dist = ConditionalFreqDist()
    for features, sentiment in [(pos_features, 'pos'), (neg_features, 'neg'), (neutral_features, 'neutral')]:
        for feature in features:
            for word in feature[0].keys():
                freq_dist.inc(word)
                cond_freq_dist[sentiment].inc(word)

    # Get most informative features
    scores = []
    features = get_most_informative_features(freq_dist, cond_freq_dist)
    for n in N_TO_TEST:
        # train a new classifier and then test accuracy
        print "Testing with %s high information features" % n
        print "-----------------------------------------"
        accuracy, classifier = evaluate_classifier(features[:n], pos_features, neg_features, neutral_features)
        scores.append((accuracy, classifier))

    classifier = sorted(scores, reverse=True)[0][1]

    # loop and classify incoming data
    context = zmq.Context.instance()
    sock = context.socket(zmq.REP)
    sock.connect('tcp://localhost:9999')
    print "Listening to ZMQ"
    while True:
        message = sock.recv()

        message_formatted = FORMATTER.process(message)
        x = {}
        for z in nltk.wordpunct_tokenize(message_formatted):
            x[z] = True

        classification = classifier.classify(x)
        classification_prob = classifier.prob_classify(x).prob(classification)
        if classification_prob > .8:
            print "[%s]: %s" % (classification, message)
        sock.send(classifier.classify(x))


if __name__ == '__main__':
    main()
