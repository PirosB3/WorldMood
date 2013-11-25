import argparse
import functools
import os

import redis
from nltk.tokenize import WhitespaceTokenizer

import phrase, data_sources
from get_formatter import FORMATTER
from get_logger import LOGGER

MIN_SCORE= 3.00


TOKENIZER = WhitespaceTokenizer().tokenize

def main(collection, destination):
    LOGGER.info("Started classifier")

    # Get training data using data source
    LOGGER.info("Building datasource")
    make_phrase = functools.partial(phrase.Phrase, tokenizer=TOKENIZER)
    ds = data_sources.RedisDataSource(redis.Redis(), collection,
        ['positive', 'negative'])
    phrases = ds.get_data(make_phrase)

    # Initialize the Text Processor, get bigrams and informative features
    LOGGER.info("Building text processor")
    processor = phrase.TextProcessor(phrases, FORMATTER)

    # Train the classifier using the Text Processor
    LOGGER.info("Training Classifier")
    classifier = processor.train_classifier(FORMATTER, MIN_SCORE, MIN_SCORE)

    # Serialize the classifier
    LOGGER.info("Serializing classifier")
    if not os.path.exists(destination):
        os.makedirs(destination)
    classifier.serialize(destination)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Train classifier from Redis')
    parser.add_argument('--collection', required=True, type=str, help='Collection used to build \
                        classifier')
    parser.add_argument('--destination', required=True, type=str, help='Destination directory')

    args = parser.parse_args()
    main(args.collection, args.destination)
