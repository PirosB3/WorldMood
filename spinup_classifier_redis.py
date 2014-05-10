import argparse
import functools
import json
import os

import zmq
from nltk.tokenize import WhitespaceTokenizer

import phrase, data_sources
from get_formatter import FORMATTER
from get_logger import LOGGER

from data_sources import *
from nltk.classify import NaiveBayesClassifier
from nltk.probability import ELEProbDist

from redis import Redis

DEFAULT_ADDRESS = '127.0.0.1'
TOKENIZER = WhitespaceTokenizer().tokenize

def get_zmq_socket(connect_address, port=9999):
    context = zmq.Context()
    sock = context.socket(zmq.REP)
    sock.connect('tcp://%s:%s' % (connect_address, port))
    return sock


def prob_dist_to_dict(prob_dist):
    res = { 'result': prob_dist.max() }
    res['probs'] = dict(map(lambda p: (p, prob_dist.prob(p)), prob_dist.samples()))
    return res

def main(path):
    LOGGER.info("Started worker")

    LOGGER.info("Loading classifier")
    make_phrase = functools.partial(phrase.Phrase, tokenizer=TOKENIZER)
    #classifier = phrase.TrainedClassifier.load(path, FORMATTER)

    r = Redis(db=7)
    feat_dist = RedisLabelFeatureDist(r)
    label_dist = ELEProbDist(RedisFreqDist(r, "classes"))
    classifier = NaiveBayesClassifier(label_dist, feat_dist)

    LOGGER.info("Ready and waiting for work")
    socket = get_zmq_socket(DEFAULT_ADDRESS)
    while True:
        try:
            message = socket.recv()
            data = json.loads(message)
            p= make_phrase(data['text'])

            result = prob_dist_to_dict(classifier.prob_classify(p.get_features(FORMATTER)))
            if not result:
                socket.send('')
                continue

            LOGGER.info("[%s] %s" % (result['result'], data['text']))
            data['prediction'] = result
            socket.send(json.dumps(data))

        except zmq.error.ZMQError as e:
            LOGGER.error("Trying to recover from ZMQError crash, sending NIL")
            socket.send('')

        except Exception as e:
            LOGGER.error(e)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Spin up one classifier worker')
    parser.add_argument('--path', required=True, type=str, help='Path used to load \
                        classifier')
    args = parser.parse_args()
    main(args.path)
