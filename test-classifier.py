import argparse
import functools
import logging

import nltk
import numpy
import pymongo
import redis
from nltk.tokenize import WhitespaceTokenizer

import phrase, data_sources
from get_formatter import FORMATTER
from get_logger import LOGGER

TOKENIZER = WhitespaceTokenizer().tokenize

def main(path, against, nodb):
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

    try:
        classifier.show_most_informative_features()
    except AttributeError:
        pass
    accuracy = nltk.classify.util.accuracy(classifier, test_data)
    LOGGER.info("Accuracy is: %s" % accuracy)

    if not nodb:
        conn = pymongo.Connection()
        db = conn['worldmood']
        coll = db['statistics']

        s = classifier.meta
        s['accuracy'] = accuracy
        s['test_corpus'] = against

        coll.update({ 'uid': classifier.get_uid() }, s, upsert=True)
        LOGGER.info("Updated collection database: %s" % s)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Test classifier')
    parser.add_argument('--path', required=True, type=str, help='Directory where serialized \
                        classifier is')
    parser.add_argument('--against', required=True, type=str, help='Redis data source to test against')
    parser.add_argument('--nodb', action='store_true', help='Disable writing to DB')

    args = parser.parse_args()
    main(args.path, args.against, args.nodb)
