from mrjob.job import MRJob
from mrjob.inline import InlineMRJobRunner

import phrase, data_sources

from get_formatter import FORMATTER
from get_logger import LOGGER

from nltk.tokenize import WhitespaceTokenizer

import redis
import functools

TOKENIZER = WhitespaceTokenizer().tokenize
SENTIMENT_MAP = {
    '"0"': 'negative',
    '"2"': 'neutral',
    '"4"': 'positive'
}

REDIS = redis.Redis(db=8)

make_phrase = functools.partial(phrase.Phrase, tokenizer=TOKENIZER)

SENTIMENT_COUNTER = "SENTIMENT_COUNTER"
SENTIMENT_IN_WORD_COUNTER = "SENTIMENT_IN_WORD_COUNTER"


class MRWordFrequencyCount(MRJob):

    def mapper(self, _, line):
        l = line.split(',')

        phrase = make_phrase(l[5])
        sentiment_name = SENTIMENT_MAP[l[0]]
        yield (SENTIMENT_COUNTER, sentiment_name), 1
        for w in phrase.get_formatted_text(FORMATTER):
            yield (SENTIMENT_IN_WORD_COUNTER, sentiment_name, w), 1

    def reducer(self, key, values):
        k = key[0]
        if k == SENTIMENT_COUNTER:
            class_name = key[1]
            n = sum(values)
            REDIS.incr("classes:keycount", 1)
            REDIS.incrby("classes:count", n)
            REDIS.hset("classes", class_name, n)
        elif k == SENTIMENT_IN_WORD_COUNTER:
            class_name, word = key[1:]
            n = sum(values)
            REDIS.hincrby("words:%s" % word, "total", n)
            REDIS.hset("words:%s" % word, class_name, n)


if __name__ == '__main__':
    MRWordFrequencyCount.run()

