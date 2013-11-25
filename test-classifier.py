import argparse
import functools
import logging

import nltk
import numpy
import redis
from nltk.classify import NaiveBayesClassifier
from nltk.corpus import stopwords
from nltk.tokenize import WhitespaceTokenizer

import phrase, data_sources
from get_formatter import FORMATTER
from get_logger import LOGGER

TOKENIZER = WhitespaceTokenizer().tokenize

def main(path, against):
    LOGGER.info("Started testing")

    LOGGER.info("Loading classifier")
    classifier = phrase.TrainedClassifier.load(path, FORMATTER)

    LOGGER.info("Loading testing data")
    make_phrase = functools.partial(phrase.Phrase, tokenizer=TOKENIZER)
    ds = data_sources.RedisDataSource(redis.Redis(), against,
        ['positive', 'negative'])
    data = ds.get_data(make_phrase)

    LOGGER.info("Making testing data")
    test_data = []
    for sentiment, phrases in data.iteritems():
        for p in phrases:
            test_data.append((p, sentiment))

    accuracy = nltk.classify.util.accuracy(classifier, test_data)
    LOGGER.info("Accuracy is: %s" % accuracy)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Test classifier')
    parser.add_argument('--path', required=True, type=str, help='Directory where serialized \
                        classifier is')
    parser.add_argument('--against', required=True, type=str, help='Redis data source to test against')

    args = parser.parse_args()
    main(args.path, args.against)
