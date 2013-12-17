import argparse
import functools
import os

import redis
from nltk.tokenize import WhitespaceTokenizer

import phrase, data_sources
from get_formatter import FORMATTER
from get_logger import LOGGER


TOKENIZER = WhitespaceTokenizer().tokenize

def generate_path_for_classifier(*args):
    root_path = os.environ.get('CLASSIFIER_ROOT_PATH', '/tmp/')
    name = '-'.join(map(str, args))
    return ''.join([root_path, name, '/'])

def main(collection, destination, nfeats, nbigrams):
    LOGGER.info("Started classifier")
    if not destination:
        destination = generate_path_for_classifier(collection, nfeats, nbigrams)
    LOGGER.info("Classifier will be saved in: %s" % destination)

    LOGGER.info("Training with %s feats and %s bigrams" % (nfeats, nbigrams))

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
    meta = {
        'train_corpus': collection
    }
    LOGGER.info("Training Classifier")
    classifier = processor.train_classifier(FORMATTER, nbigrams, nfeats, meta)

    # Serialize the classifier
    LOGGER.info("Serializing classifier")
    if not os.path.exists(destination):
        os.makedirs(destination)
    classifier.serialize(destination)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Train classifier from Redis')
    parser.add_argument('--collection', required=True, type=str, help='Collection used to build \
                        classifier')
    parser.add_argument('--destination', required=False, type=str, help='Destination directory')
    parser.add_argument('--feats', type=int, default=10000, help='Number of informative features')
    parser.add_argument('--bigrams', type=int, default=3000, help='Number of informative bigrams')

    args = parser.parse_args()
    main(args.collection, args.destination, args.feats, args.bigrams)
